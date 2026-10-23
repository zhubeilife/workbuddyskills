#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sync_check.py —— 拆分后两个技能包的「共用资产一致性」校验器。

背景
----
「家长会发言稿」与「日常家校沟通话术」两个技能包各自独立、可单独分发，
但下面这批资产是**两边共用**的（内容必须逐字节一致）：

    references/redlines.md
    scripts/check_tone.py
    scripts/check_advice.py
    scripts/check_policy.py
    scripts/check_docx.py
    scripts/check_meta.py
    scripts/CHANGELOG.md

任一边改了红线规则或修了脚本误报，另一边必须同步。
本脚本就是防止「改了一边、忘了另一边」的机械兜底。

用法
----
    python sync_check.py            # 人类可读输出
    python sync_check.py --json     # 供管道用

退出码：0 = 全部一致；1 = 发现不一致（**必须同步后再交付**）；2 = 目标目录缺失。

⚠️ 本脚本只做文件比对，不自动覆盖——哪边是新版由人判断，避免把旧版盖回去。
"""

import os
import sys
import json
import hashlib

SKILL_A = "cnki-edu-parent-meeting-speech"      # 发言稿
SKILL_B = "cnki-edu-daily-comm-scripts"         # 日常话术

# 共用资产（相对技能包根目录）
SHARED = [
    os.path.join("references", "redlines.md"),
    os.path.join("scripts", "check_tone.py"),
    os.path.join("scripts", "check_advice.py"),
    os.path.join("scripts", "check_policy.py"),
    os.path.join("scripts", "check_docx.py"),
    os.path.join("scripts", "check_meta.py"),
    os.path.join("scripts", "CHANGELOG.md"),
]


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve_base():
    """从本脚本位置反推 skills 根目录：.../skills/<skill-name>/scripts/sync_check.py"""
    here = os.path.dirname(os.path.abspath(__file__))
    scripts_dir = os.path.basename(here)
    if scripts_dir != "scripts":
        return None
    skill_dir = os.path.dirname(here)
    return os.path.dirname(skill_dir)


def main():
    base = resolve_base()
    if base is None:
        print("[跳过] 本脚本不在 <skill>/scripts/ 下，无法定位同级技能包。")
        return 2

    dir_a = os.path.join(base, SKILL_A)
    dir_b = os.path.join(base, SKILL_B)

    missing_root = [d for d in (dir_a, dir_b) if not os.path.isdir(d)]
    if missing_root:
        print("[不通过] 以下技能目录不存在：")
        for d in missing_root:
            print("   ", d)
        return 2

    ok, diff, miss = [], [], []
    for rel in SHARED:
        pa, pb = os.path.join(dir_a, rel), os.path.join(dir_b, rel)
        if not (os.path.isfile(pa) and os.path.isfile(pb)):
            miss.append((rel, os.path.isfile(pa), os.path.isfile(pb)))
            continue
        ha, hb = md5(pa), md5(pb)
        size_a, size_b = os.path.getsize(pa), os.path.getsize(pb)
        if ha == hb:
            ok.append({"file": rel, "md5": ha, "size": size_a})
        else:
            diff.append({"file": rel, "md5_a": ha, "md5_b": hb,
                         "size_a": size_a, "size_b": size_b})

    if "--json" in sys.argv:
        print(json.dumps({"ok": ok, "diff": diff, "missing": miss},
                         ensure_ascii=False, indent=2))
        return 1 if (diff or miss) else 0

    print("=" * 62)
    print("共用资产同步校验")
    print("  A:", dir_a)
    print("  B:", dir_b)
    print("=" * 62)

    for it in ok:
        print("  [一致] %-38s %s" % (it["file"], it["md5"][:8]))

    for rel, has_a, has_b in miss:
        print("  [缺失] %-38s A=%s B=%s" % (rel, has_a, has_b))

    for it in diff:
        print("  [不一致] %s" % it["file"])
        print("            A: md5=%s  %d bytes" % (it["md5_a"][:12], it["size_a"]))
        print("            B: md5=%s  %d bytes" % (it["md5_b"][:12], it["size_b"]))

    print("-" * 62)
    if diff or miss:
        print("[不通过] %d 项一致，%d 项不一致，%d 项缺失。" % (len(ok), len(diff), len(miss)))
        print("         请把较新的一份复制到另一边（人工确认哪边是新版），再跑一次。")
        print("         本脚本不自动覆盖——避免把旧版盖回去。")
        return 1

    print("[通过] %d 项共用资产全部一致。" % len(ok))
    return 0


if __name__ == "__main__":
    sys.exit(main())
