# -*- coding: utf-8 -*-
"""题库适配器：把 CNKI 基础教育题库（edu MCP tkSearchQuestion 返回）直接变成作业设计单。

用法：
  python bank_to_items.py --bank bank_raw.json --sids SID1,SID2 \
      --subject 数学 --stage "小学中高段(3-6)" \
      --std "《义务教育数学课程标准（2022年版）》第三学段『数据的收集、整理与表达』…" \
      --literacy "数据意识、应用意识" \
      --out OUTDIR

说明：
  - bank_raw.json 是 tkSearchQuestion 返回里的 data 数组（[{SID,Content,CateName,Label,Degree,...}, ...]）。
  - 题库 Content 是带 <table class="edittable"> 的 HTML：本适配器把它解析成真正的
    结构化 table 字段（不再手动抄数、不再编造数字），并保留导语与 (1)(2)(3) 子问题。
  - 每道题 origin=retrieve、source_id=题库 SID、source_label=题库 Label，validate --plan
    事实级核对直接通过（source_id 落在计划 bank_id 内）。
  - 题库真题答案优先用 tkQuestionAnalysis 回查官方答案与解析（传 --analysis 时自动回填到
    item 的 answer/analysis/points，题面仍一字不改）；未传 --analysis 时在教师参考里提示回查原卷/题库。
"""
import re
import json
import argparse
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mcp_adapters as ma  # 复用 strip_html / normalize_analysis / fill_item_with_analysis

# ----------------------------- HTML 清洗 -----------------------------
BR = re.compile(r"<br\s*/?>", re.I)
DEL = re.compile(r"<del>(.*?)</del>", re.S | re.I)
BLANK = re.compile(r"<!--BA-->.*?<!--EA-->", re.S)   # 题库填空标记（中间多为空）
TAG = re.compile(r"<[^>]+>")
WS = re.compile(r"[ \t\u00a0]+")


def _clean(text):
    """清洗一段 HTML 文本：去 <del>、去 <img>、填空标记→（ ）、去标签、HTML 反转义。"""
    if not text:
        return ""
    text = BR.sub("\n", text)
    text = DEL.sub(r"\1", text)            # 保留 <del> 内文字（如「废旧电池」是题面正常词）
    text = BLANK.sub("", text)             # 去掉填空标记，保留外层 （） 括号
    text = re.sub(r"（）", "（ ）", text)  # 外层空括号 → 中文填空括号
    text = re.sub(r"<img\b[^>]*>", "", text, flags=re.I)  # 配图（如折线图）在作业单里去掉，教师按数据重绘
    text = TAG.sub("", text)
    text = text.replace("&nbsp;", " ")
    try:
        import html as _h
        text = _h.unescape(text)
    except Exception:
        pass
    text = WS.sub(" ", text)
    # 合并多余空行
    lines = [ln.strip() for ln in text.split("\n")]
    out = []
    for ln in lines:
        if ln:
            out.append(ln)
    return "\n".join(out).strip()


def _clean_cell(cell_html):
    """清洗单元格：<br>→换行，其余与 _clean 同，但单元格内不去掉结构。"""
    s = BR.sub("\n", cell_html)
    s = DEL.sub(r"\1", s)
    s = BLANK.sub("", s)
    s = re.sub(r"（）", "（ ）", s)
    s = re.sub(r"<img\b[^>]*>", "", s, flags=re.I)
    s = TAG.sub("", s)
    s = s.replace("&nbsp;", " ")
    try:
        import html as _h
        s = _h.unescape(s)
    except Exception:
        pass
    s = WS.sub(" ", s)
    return s.strip()


IMG_TAG = re.compile(r"<img\b[^>]*>", re.I)
IMG_SRC = re.compile(r"src\s*=\s*[\"']([^\"']+)[\"']", re.I)
IMG_ALT = re.compile(r"alt\s*=\s*[\"']([^\"']*)[\"']", re.I)


def _download_images(content, out_dir, timeout=25):
    """抽取 Content 里的 <img> 并下载到 out_dir/figures/，返回 figures 列表。

    每项为 {path(绝对路径), caption, after}；下载失败则 path 保留原始 URL 并标记 url=True，
    供下游降级为占位文字（绝不静默丢弃——早期版本直接删 <img> 导致原题折线图丢失）。
    """
    figs = []
    if not out_dir:
        return figs
    figdir = os.path.join(out_dir, "figures")
    os.makedirs(figdir, exist_ok=True)
    for k, m in enumerate(re.finditer(IMG_TAG, content), 1):
        tag = m.group()
        src = IMG_SRC.search(tag)
        if not src:
            continue
        url = src.group(1).strip()
        if url.startswith("//"):
            url = "http:" + url
        alt = IMG_ALT.search(tag)
        cap = (alt.group(1).strip() if alt else "") or "原题附图"
        if cap in ("菁优网", "jyeoo", "菁优", "ques", "question"):
            cap = "原题附图"
        ext = ".png"
        me = re.search(r"\.([a-zA-Z0-9]+)(?:[?#]|$)", url)
        if me and me.group(1).lower() in ("png", "jpg", "jpeg", "gif", "svg", "webp", "bmp"):
            ext = "." + me.group(1).lower()
        fname = "fig%d%s" % (k, ext)
        fpath = os.path.abspath(os.path.join(figdir, fname))
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
            with open(fpath, "wb") as fh:
                fh.write(data)
            figs.append({"path": fpath, "caption": cap, "after": "question"})
            print("  下载原图 %s → %s (%d 字节)" % (url, fname, len(data)))
            # 防线：题库外链图（如 jyeoo）像素/元数据里常带第三方平台署名水印，
            # 直接嵌入会把它印进成品。命中即告警，要求先用真实数据本地重绘替换。
            blob = data
            for kw in ("菁优网".encode("utf-8"), b"jyeoo", b"JYEOO", b"Jyeoo"):
                if kw in blob:
                    print("  !! 警告：原图含第三方平台水印（%s），禁止直接嵌入！"
                          "请按题目真实数据用 matplotlib 本地重绘并覆盖 %s"
                          % (kw.decode("utf-8", "replace"), fpath), file=sys.stderr)
                    break
        except Exception as e:
            print("  ! 原图下载失败 %s：%s" % (url, e), file=sys.stderr)
            figs.append({"path": url, "caption": cap, "after": "question", "url": True})
    return figs


def parse_tables(content):
    """解析所有 <table class="edittable">，返回 list[ [ [cell,...], ... ] ]（每行一个 list）。"""
    tables = []
    for m in re.finditer(r"<table[^>]*class=\"edittable\"[^>]*>(.*?)</table>", content, re.S | re.I):
        body = m.group(1)
        rows = []
        for tr in re.finditer(r"<tr[^>]*>(.*?)</tr>", body, re.S | re.I):
            cells = []
            for td in re.finditer(r"<t[dh][^>]*>(.*?)</t[dh]>", tr.group(1), re.S | re.I):
                cells.append(_clean_cell(td.group(1)))
            if cells:
                rows.append(cells)
        if rows:
            tables.append(rows)
    return tables


def split_subquestions(text):
    """把『（1）…（2）…（3）…』拆成 ['（1）…', '（2）…', '（3）…']。

    仅当 （数字） 出现在句首/句号/分号/前导括号之后才算小题号，
    排除『五（2）班』这类班级编号里的 （2）。
    """
    markers = [(m.start(), m.group()) for m in re.finditer(r"（\d+）", text)]
    real = []
    for pos, mk in markers:
        prev = text[pos - 1] if pos > 0 else ""
        if prev == "" or prev in "。\n；（）" or prev.isspace():
            real.append((pos, mk))
    if not real:
        return [text.strip()] if text.strip() else []
    qs = []
    for k, (pos, mk) in enumerate(real):
        start = pos + len(mk)
        end = real[k + 1][0] if k + 1 < len(real) else len(text)
        seg = text[start:end].strip()
        if seg:
            qs.append(mk + seg)
    return qs


def bank_item_to_homework(b, level="基础", dur=8, std_aligned="", literacy=None, out_dir=None):
    """单个题库 item(dict) → 作业设计 item(dict)。out_dir 用于下载并落盘原题附图。"""
    content = b.get("Content", "") or ""
    tables = parse_tables(content)

    # 导语：第一个表格之前的文本
    pre = re.split(r"<table", content, maxsplit=1, flags=re.I)[0]
    intro = _clean(pre)

    # 子问题：最后一个表格之后的文本
    if "</table>" in content:
        post = content.rsplit("</table>", 1)[-1]
    else:
        post = ""
    post_txt = _clean(post)
    qs = split_subquestions(post_txt) if post_txt else []

    item = {
        "id": "1",
        "level": level,
        "type": (b.get("CateName") or "").strip() or "解答题",
        "cognitive": "理解",
        "origin": "retrieve",
        "dur": int(dur),
        "source_id": (b.get("SID") or "").strip(),
        "source_label": (b.get("Label") or "").strip(),
        "points": "",
        "stem": intro,
    }
    if tables:
        rows = tables[0]  # 多表时取第一张（主数据表）；其余表可后续扩展
        item["table"] = {"head": rows[0], "rows": rows[1:]}
    if qs:
        item["questions"] = qs
    figs = _download_images(content, out_dir) if out_dir else []
    if figs:
        item["figures"] = figs
    return item


def main():
    ap = argparse.ArgumentParser(description="题库 HTML → 作业设计 items.json / plan.json")
    ap.add_argument("--bank", required=True, help="题库原始 JSON（tkSearchQuestion 的 data 数组或含 data 的对象）")
    ap.add_argument("--sids", help="逗号分隔的 SID 白名单；不给则用 bank 里全部题")
    ap.add_argument("--subject", default="数学")
    ap.add_argument("--stage", default="小学中高段(3-6)")
    ap.add_argument("--grade", default="")
    ap.add_argument("--unit", default="")
    ap.add_argument("--topic", default="题库原题作业")
    ap.add_argument("--std", default="", help="课标对齐文本（validate 必填）")
    ap.add_argument("--literacy", default="", help="逗号分隔的核心素养")
    ap.add_argument("--level", default="基础")
    ap.add_argument("--dur", type=int, default=8)
    ap.add_argument("--analysis", default="", help="tkQuestionAnalysis 原始/标准化结果 JSON；传入即回填官方答案与解析")
    ap.add_argument("--out", required=True, help="输出目录")
    args = ap.parse_args()

    raw = json.load(open(args.bank, encoding="utf-8"))
    if isinstance(raw, dict):
        raw = raw.get("data") or raw.get("items") or (raw.get("item") and [raw["item"]]) or []
    if not isinstance(raw, list):
        print("bank 文件不是数组，退出", file=sys.stderr)
        sys.exit(2)

    want = set(s.strip() for s in (args.sids or "").split(",") if s.strip())
    picked = [b for b in raw if (not want or (b.get("SID") or "").strip() in want)]
    if not picked:
        print("未选中任何题库题目（sids=%s，bank 共 %d 题）" % (args.sids, len(raw)), file=sys.stderr)
        sys.exit(3)

    items = []
    plan_items = []
    os.makedirs(args.out, exist_ok=True)  # 先建目录，图片才能下载落盘
    for idx, b in enumerate(picked, 1):
        it = bank_item_to_homework(b, level=args.level, dur=args.dur,
                                    std_aligned=args.std, literacy=None, out_dir=args.out)
        it["id"] = str(idx)
        items.append(it)
        plan_items.append({
            "mode": "retrieve",
            "bank_id": (b.get("SID") or "").strip(),
            "label": (b.get("Label") or "").strip(),
        })

    # 回填官方解析（可选）：--analysis 指向 tkQuestionAnalysis 原始/标准化结果
    if args.analysis:
        norm = ma.load_analysis_any(args.analysis)
        by_sid = {(a.get("sid") or "").strip(): a for a in norm
                  if (a.get("sid") and (a.get("body") or a.get("answer")))}
        n_fill = 0
        for it in items:
            a = by_sid.get((it.get("source_id") or "").strip())
            if a and ma.fill_item_with_analysis(it, a):
                n_fill += 1
        print("  官方解析回填 %d 题" % n_fill)

    meta = {"std_aligned": args.std}
    if args.literacy:
        meta["literacy"] = [x.strip() for x in args.literacy.split("、") if x.strip()]
    if args.analysis:
        meta["notes"] = ["本作业全部为题库原题（retrieve），题面一字不改；官方答案与解析已通过 tkQuestionAnalysis 回查题库官方解析。"]
    else:
        meta["notes"] = ["本作业全部为题库原题（retrieve），题面一字不改；答案与解析请回查原卷/题库。"]
    if args.grade or args.unit:
        meta["notes"].append("适用：%s%s" % (args.grade and (args.grade + " ") or "", args.unit))

    params = {
        "subject": args.subject,
        "stage": args.stage,
        "grade": args.grade,
        "unit": args.unit,
        "topic": args.topic,
        "job_type": "课时作业",
        "supply": "retrieve",
        "total_count": len(items),
        "ratio": {args.level: len(items)},
        "max_minutes": sum(i["dur"] for i in items),
        "std_aligned": args.std,
        "literacy": meta.get("literacy", []),
    }
    plan = {"gen_max": 0, "items": plan_items}

    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "items.json"), "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "items": items}, f, ensure_ascii=False, indent=2)
    with open(os.path.join(args.out, "params.json"), "w", encoding="utf-8") as f:
        json.dump(params, f, ensure_ascii=False, indent=2)
    with open(os.path.join(args.out, "plan.json"), "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)

    print("已生成 %d 题 → %s" % (len(items), args.out))
    for it in items:
        t = it.get("table")
        print("  - [%s] %s｜table=%s 行%d 列%d｜questions=%d"
              % (it["id"], it["type"], "有" if t else "无",
                  len(t["rows"]) if t else 0, len(t["head"]) if t else 0,
                  len(it.get("questions", []))))


if __name__ == "__main__":
    main()
