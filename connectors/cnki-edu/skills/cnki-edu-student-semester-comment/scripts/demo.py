# -*- coding: utf-8 -*-
"""一键跑通整条链路，用于自测/演示。

会依次执行：造示例材料 → 材料对齐 → 造模板基线 → 雷同度对比自检 → 出评语表。
全部产物落在 --out 目录（默认 ./demo）。

用法：
  python demo.py                 # 完整演示
  python demo.py --out 我的演示
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def run(title, args):
    print("\n" + "=" * 62)
    print("▶ " + title)
    print("=" * 62)
    r = subprocess.run([sys.executable] + args, cwd=HERE)
    if r.returncode != 0:
        sys.exit("步骤失败：" + title)


def main():
    try:
        import openpyxl  # noqa: F401
    except ImportError:
        sys.exit("本演示链路需要 openpyxl，请先安装：pip install openpyxl")
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="demo")
    args = ap.parse_args()
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    p = lambda n: os.path.join(out, n)
    s = lambda n: os.path.join(HERE, n)

    run("Step 2-1 生成六类示例材料",
        [s("make_sample_data.py"), "--out", out])

    run("Step 2-2 第一段 · 材料对齐",
        [s("prepare_roster.py"),
         "--scores", p("示例_成绩表.xlsx"),
         "--homework", p("示例_作业统计表.xlsx"),
         "--classroom", p("示例_课堂表现统计表.xlsx"),
         "--notes", p("示例_教师个别描述.xlsx"),
         "--past-comments", p("示例_往年评语.xlsx"),
         "--awards", p("示例_奖状荣誉.xlsx"),
         "--class-name", "初二(3)班", "--exam-name", "初二上学期期末考试",
         "--out", p("roster.json")])

    run("Step 5-1 生成模板写法对照组",
        [s("make_naive_baseline.py"), "--roster", p("roster.json"),
         "--out", p("comments_naive.json")])

    ex = os.path.join(HERE, "..", "references", "comments.json")
    if os.path.exists(ex):
        import shutil
        shutil.copy(ex, p("comments.json"))
        print("\n(已从 references/ 取用一份填好评语的 comments.json 作为示范)")
    else:
        print("\n[提示] 未找到示例评语。真实使用时，此步骤由你(AI)撰写 comments.json。")
        return

    run("Step 5-2 雷同度自检（含对照组 + 往年评语重合）",
        [s("similarity_check.py"),
         "--comments", p("comments.json"), "--tag", "规则驱动（本skill）",
         "--comments-too", p("comments_naive.json"), "--tag-too", "模板写法（对照组）",
         "--past", p("roster.json"),
         "--out", p("雷同度报告.md"), "--json", p("雷同度报告.json")])

    run("Step 6 出评语表",
        [s("export_comments.py"), "--roster", p("roster.json"),
         "--comments", p("comments.json"),
         "--out", p("评语表.xlsx"),
         "--min-len", "120", "--max-len", "180"])

    print("\n" + "=" * 62)
    print("全部完成，产物目录：" + out)
    print("=" * 62)


if __name__ == "__main__":
    main()
