#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI 组卷 · 知识点树缓存与归一化辅助（仅缓存「元数据」，合规）

目的：把 `tkPoint(subjectCode)` 拉回的全量知识点树**落盘缓存**，二次组卷直接读盘，
      不再重复调用，并提供一个「教材知识点 → 库标准考点名」的模糊匹配器，
      把 S3.5 的「大轮 LLM 语义匹配」尽量降为「查表 / 候选筛选」。

缓存内容仅为**知识点元数据（考点名）**，不含任何试题题干/答案 → 不触碰合规红线。

命令：
    # 1) 保存：把 tkPoint 工具返回的原始 JSON 落盘 -> 展平 -> 叶名清单
    python3 tkpoint_cache.py save <raw_tkpoint.json> --subject-code 33

    # 2) 列出缓存状态
    python3 tkpoint_cache.py status

    # 3) 查看某学科叶名（可选 grep）
    python3 tkpoint_cache.py names --subject-code 33 [--grep 方程]

    # 4) 模糊匹配（细目表知识点 → 候选库标准考点名）
    python3 tkpoint_cache.py map --subject-code 33 --points "一元一次方程,等式的性质"
    python3 tkpoint_cache.py map --subject-code 33 --points-file points.txt

    # 5) prep：S3.5「一次到位」——一次调用同时返回缓存状态 + 叶名 / 映射候选
    #    （把原本 status + names/map 的两三次模型往返压成 1 轮）
    python3 tkpoint_cache.py prep --subject-code 33
    python3 tkpoint_cache.py prep --subject-code 33 --points "光合作用,细胞呼吸"
"""
import os, sys, json, argparse, difflib, datetime

DEFAULT_CACHE = os.environ.get(
    "ZJ_CACHE_DIR", os.path.expanduser("~/.workbuddy/cache/cnki-edu-ai-zujuan-paper/tkpoint"))


def _cache_paths(cache_dir, subject):
    return (os.path.join(cache_dir, f"tkpoint_{subject}.json"),
            os.path.join(cache_dir, f"tkpoint_{subject}_leafnames.txt"))


def _flatten(nodes, all_names, leaf_names):
    for n in nodes or []:
        if not isinstance(n, dict):
            continue
        name = (n.get("Name") or n.get("name") or "").strip()
        children = n.get("Children") or n.get("children") or []
        if name and "<" not in name and len(name) <= 40:
            all_names.append(name)
            if not children:
                leaf_names.append(name)
        if children:
            _flatten(children, all_names, leaf_names)


def _extract_nodes(raw):
    if isinstance(raw, dict):
        for k in ("data", "Data", "result", "Result"):
            if k in raw:
                return raw[k]
        return []
    return raw


def _load_cache(cache_dir, subject):
    p, _ = _cache_paths(cache_dir, subject)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def cmd_save(args):
    with open(args.raw, encoding="utf-8") as f:
        raw = json.load(f)
    nodes = _extract_nodes(raw)
    all_names, leaf_names = [], []
    _flatten(nodes, all_names, leaf_names)
    all_names = list(dict.fromkeys(all_names))
    leaf_names = list(dict.fromkeys(leaf_names))
    os.makedirs(args.cache_dir, exist_ok=True)
    p, leafp = _cache_paths(args.cache_dir, args.subject_code)
    payload = {
        "subjectCode": args.subject_code,
        "saved_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "count_all": len(all_names),
        "count_leaf": len(leaf_names),
        "all_names": all_names,
        "leaf_names": leaf_names,
    }
    with open(p, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    with open(leafp, "w", encoding="utf-8") as f:
        f.write("\n".join(leaf_names))
    print(f"[tkpoint_cache] 已缓存 subject {args.subject_code}: "
          f"{len(all_names)} 节点 / {len(leaf_names)} 叶名 → {p}")


def cmd_status(args):
    if not os.path.isdir(args.cache_dir):
        print("[tkpoint_cache] 无缓存目录（尚未缓存任何学科）")
        return
    rows = []
    for fn in sorted(os.listdir(args.cache_dir)):
        if fn.startswith("tkpoint_") and fn.endswith(".json"):
            with open(os.path.join(args.cache_dir, fn), encoding="utf-8") as f:
                d = json.load(f)
            rows.append((d.get("subjectCode"), d.get("count_all"),
                         d.get("count_leaf"), d.get("saved_at")))
    if not rows:
        print("[tkpoint_cache] 缓存为空")
        return
    print("subject  节点数  叶名数  缓存时间")
    for s, a, l, t in rows:
        print(f"{s:<8} {a:<6} {l:<6} {t}")


def cmd_names(args):
    d = _load_cache(args.cache_dir, args.subject_code)
    if not d:
        print(f"[tkpoint_cache] 未缓存 subject {args.subject_code}，请先 save", file=sys.stderr)
        raise SystemExit(1)
    names = d["leaf_names"]
    if args.grep:
        names = [n for n in names if args.grep in n]
    print(f"# subject {args.subject_code} 叶名 {len(names)} 条"
          + (f"（grep={args.grep}）" if args.grep else ""))
    for n in names:
        print(n)


def cmd_map(args):
    d = _load_cache(args.cache_dir, args.subject_code)
    if not d:
        print(f"[tkpoint_cache] 未缓存 subject {args.subject_code}，请先 save", file=sys.stderr)
        raise SystemExit(1)
    pool = d["leaf_names"] or d["all_names"]
    if args.points_file:
        with open(args.points_file, encoding="utf-8") as f:
            inputs = [ln.strip() for ln in f if ln.strip()]
    else:
        inputs = [s.strip() for s in (args.points or "").split(",") if s.strip()]

    out = []
    for w in inputs:
        subs = [n for n in pool if (w in n or n in w)]
        close = difflib.get_close_matches(w, pool, n=args.top, cutoff=args.cutoff)
        cand = list(dict.fromkeys(subs + close))[:args.top]
        out.append({"input": w, "matches": cand, "best": cand[0] if cand else None})
    print(json.dumps(out, ensure_ascii=False, indent=1))


def _match_points(pool, inputs, top, cutoff):
    out = []
    for w in inputs:
        subs = [n for n in pool if (w in n or n in w)]
        close = difflib.get_close_matches(w, pool, n=top, cutoff=cutoff)
        cand = list(dict.fromkeys(subs + close))[:top]
        out.append({"input": w, "matches": cand, "best": cand[0] if cand else None})
    return out


def cmd_prep(args):
    """S3.5 一次到位：把「缓存状态」与「叶名 / 映射候选」合并成单次调用。

    - 未缓存 → 输出 {"cached": false} 并退出码 1（编排层据此决定是否 tkPoint 落盘）。
    - 已缓存且未给 --points → 输出叶名全集（供 AI 提名）。
    - 已缓存且给了 --points → 输出映射候选（省掉单独的 map 调用）。
    """
    d = _load_cache(args.cache_dir, args.subject_code)
    if not d:
        print(json.dumps({
            "cached": False,
            "subjectCode": args.subject_code,
            "hint": "未缓存：先调 tkPoint(subjectCode) 拉全量树 → tkpoint_cache.py save <raw.json> --subject-code %d" % args.subject_code,
        }, ensure_ascii=False, indent=1))
        raise SystemExit(1)

    inputs = []
    if args.points_file:
        with open(args.points_file, encoding="utf-8") as f:
            inputs = [ln.strip() for ln in f if ln.strip()]
    elif args.points:
        inputs = [s.strip() for s in args.points.split(",") if s.strip()]

    info = {
        "cached": True,
        "subjectCode": args.subject_code,
        "count_all": d.get("count_all"),
        "count_leaf": d.get("count_leaf"),
        "saved_at": d.get("saved_at"),
    }
    if inputs:
        pool = d["leaf_names"] or d["all_names"]
        info["mode"] = "map"
        info["map"] = _match_points(pool, inputs, args.top, args.cutoff)
    else:
        info["mode"] = "names"
        info["leaf_names"] = d["leaf_names"]
    print(json.dumps(info, ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser(description="知识点树缓存与归一化辅助")
    ap.add_argument("--cache-dir", default=DEFAULT_CACHE)
    sub = ap.add_subparsers(dest="cmd", required=True)

    ps = sub.add_parser("save", help="保存并展平 tkPoint 原始 JSON")
    ps.add_argument("raw")
    ps.add_argument("--subject-code", type=int, required=True)
    ps.set_defaults(func=cmd_save)

    ps = sub.add_parser("status", help="列出已缓存学科")
    ps.set_defaults(func=cmd_status)

    ps = sub.add_parser("names", help="查看叶名")
    ps.add_argument("--subject-code", type=int, required=True)
    ps.add_argument("--grep", default="")
    ps.set_defaults(func=cmd_names)

    ps = sub.add_parser("map", help="模糊匹配细目表知识点")
    ps.add_argument("--subject-code", type=int, required=True)
    ps.add_argument("--points", default="")
    ps.add_argument("--points-file", default="")
    ps.add_argument("--top", type=int, default=5)
    ps.add_argument("--cutoff", type=float, default=0.5)
    ps.set_defaults(func=cmd_map)

    ps = sub.add_parser("prep", help="S3.5 一次到位：状态 + 叶名/映射")
    ps.add_argument("--subject-code", type=int, required=True)
    ps.add_argument("--points", default="")
    ps.add_argument("--points-file", default="")
    ps.add_argument("--top", type=int, default=5)
    ps.add_argument("--cutoff", type=float, default=0.5)
    ps.set_defaults(func=cmd_prep)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
