# -*- coding: utf-8 -*-
"""
学科硬约束常量校验（离线，零依赖）。

比对生成 HTML 里 <span data-fact="名称">数值</span> 标记的数字，
与 references/_facts.json 的权威值是否在容差内一致。

用法：
    python lint_facts.py <文件.html> [文件2 ...]

退出码：0 = 通过或无可查标记；1 = 有数值不一致。
"""
import sys
import os
import re
import json

HERE = os.path.dirname(os.path.abspath(__file__))
FACTS_PATH = os.path.join(HERE, "..", "references", "_facts.json")

# 上标数字 → 普通数字
SUP = {"\u2070": "0", "\u00b9": "1", "\u00b2": "2", "\u00b3": "3",
       "\u2074": "4", "\u2075": "5", "\u2076": "6", "\u2077": "7",
       "\u2078": "8", "\u2079": "9", "\u207a": "+", "\u207b": "-"}


def load_facts():
    try:
        with open(FACTS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:  # noqa
        print("[警告] 无法读取 _facts.json：%s" % e)
        return {}


def norm_num(s):
    """把文本里的上标/特殊字符转成可解析的数字文本。"""
    s = "".join(SUP.get(ch, ch) for ch in s)
    s = s.replace("\u00d7", "*").replace("x", "*")  # × / x → *
    s = s.replace("\u2236", ":").replace("\uff1a", ":")  # ∶ / ： → :
    s = s.replace("\u2070", "0")
    return s


def extract_scalar(text):
    t = norm_num(text)
    # 科学计数：3*10^8 或 3e8
    m = re.search(r"(-?\d+(?:\.\d+)?)\s*\*\s*10\s*[\^]?\s*(-?\d+)", t)
    if m:
        try:
            return float(m.group(1)) * (10 ** int(m.group(2)))
        except Exception:
            return None
    m = re.search(r"(-?\d+(?:\.\d+)?)\s*[eE]\s*(-?\d+)", t)
    if m:
        try:
            return float(m.group(1)) * (10 ** int(m.group(2)))
        except Exception:
            return None
    m = re.search(r"(-?\d+(?:\.\d+)?)", t)
    return float(m.group(1)) if m else None


def extract_ratio(text):
    t = norm_num(text)
    m = re.search(r"(-?\d+(?:\.\d+)?)\s*:\s*(-?\d+(?:\.\d+)?)", t)
    if m:
        a, b = float(m.group(1)), float(m.group(2))
        if b != 0:
            return a / b
    return None


def check_file(path, facts):
    if not os.path.isfile(path):
        print("[错误] 文件不存在：%s" % path)
        return 1
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        html = f.read()

    # 收集所有 data-fact 标记
    marks = re.findall(r'<[^>]*\bdata-fact\s*=\s*["\']([^"\']+)["\'][^>]*>([\s\S]*?)</', html)
    if not marks:
        print("  %s — SKIP（无 data-fact 标记）" % os.path.basename(path))
        return 0

    fails = 0
    print("  %s — 找到 %d 个 data-fact 标记：" % (os.path.basename(path), len(marks)))
    for name, inner in marks:
        entry = None
        for subj, table in facts.items():
            if name in table:
                entry = table[name]
                break
        if not entry:
            print("    · %s — 信息（_facts.json 无此名称，跳过）" % name)
            continue
        kind = entry.get("kind", "scalar")
        tol = float(entry.get("tol", 0))
        if kind == "flag":
            print("    · %s — 信息（flag 仅参考，跳过）" % name)
            continue
        if kind == "ratio":
            got = extract_ratio(inner)
            want = float(entry["a"]) / float(entry["b"]) if entry.get("b") else None
            ok = got is not None and want is not None and abs(got - want) <= tol
            detail = "实际 %s 期望 %s:%s" % (inner.strip()[:20], entry.get("a"), entry.get("b"))
        else:
            got = extract_scalar(inner)
            want = entry.get("value")
            ok = got is not None and want is not None and abs(got - float(want)) <= float(tol)
            detail = "实际 %s 期望 %s%s（容差%s）" % (
                inner.strip()[:24], want, entry.get("unit", ""), tol)
        if ok:
            print("    PASS  %s — %s" % (name, detail))
        else:
            fails += 1
            print("    FAIL  %s — %s" % (name, detail))
    return 1 if fails else 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    facts = load_facts()
    if not facts:
        print("[错误] _facts.json 为空或缺失，无法校验。")
        return 2
    rc = 0
    print("=" * 56)
    print("学科硬约束常量校验（lint_facts）")
    print("=" * 56)
    for p in sys.argv[1:]:
        rc = check_file(p, facts) or rc
    print("=" * 56)
    if rc:
        print("结果：存在数值不一致，请核对。")
    else:
        print("结果：通过（或无可查标记）。")
    return rc


if __name__ == "__main__":
    sys.exit(main())
