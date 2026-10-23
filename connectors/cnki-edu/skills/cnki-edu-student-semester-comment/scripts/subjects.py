# -*- coding: utf-8 -*-
"""学科词典与同义归一 —— 四个脚本共用的唯一来源。

为什么单独抽出来：原先 prepare_roster / export_comments / similarity_check /
adapt_exam_workbook 各自维护了一份学科词表，四份内容互不相同
（「道法」只出现在其中两份，「道德与法治」在另外两份里根本没有），
于是同一门课在不同环节的判定口径不一致，实测踩到两次：

  · 成绩表列名写「道法」→ prepare_roster 整列被忽略，
    该科不进学科集，班均与学科偏差全部算歪（其余各科被顶上来当「优势/短板」）
  · 评语正文写「道法考了 85」→ export_comments 的分数检测漏报，
    因为它的词表里没有「道法」

所以把词表与归一规则收到一处，四个脚本都从这里取。

一条口径说明：**同义归一只用于「判断两列是不是同一门课」，不改写输出。**
用户表里列名叫「道法」，roster 与交付表就照样写「道法」；
归一后的本体名（「道德与法治」）只在去重、跨列比对、骨架归一这类内部判断里用。
"""

# 列名里含其中任一词即视为学科列（子串匹配：「语文」「语文成绩」「期末语文」都能命中）
SUBJECT_POOL = [
    "语文", "数学", "英语", "物理", "化学", "生物", "政治", "历史", "地理",
    "道德与法治", "道法", "德法", "科学", "体育", "音乐", "美术", "信息技术", "劳动",
]

# 同义写法 → 学科本体。一个本体可以对应多个写法。
SUBJECT_ALIAS = {
    "道法": "道德与法治",   # 义务教育阶段最常用的简称
    "德法": "道德与法治",   # 部分地区用这个写法
}


def canonical(word):
    """把命中的学科词收敛成学科本体；非学科词原样返回。"""
    return SUBJECT_ALIAS.get(word, word)


def subject_bases(text):
    """返回这段文本（列名或正文片段）命中的**学科本体**集合。

    归一在这里生效，所以「道法」与「道德与法治」得到同一个本体，
    可以直接用集合是否有交集来判断「是不是同一门课」。
    """
    if not text:
        return set()
    return {canonical(s) for s in SUBJECT_POOL if s in str(text)}


def has_subject_word(text):
    """这段文本里是否出现了学科词。"""
    return bool(subject_bases(text))


if __name__ == "__main__":
    # 自检：同义写法必须收敛到同一本体
    assert subject_bases("道法") == subject_bases("道德与法治") == {"道德与法治"}
    assert subject_bases("期中道德与法治") == {"道德与法治"}
    assert subject_bases("道法成绩") == {"道德与法治"}
    assert canonical("道法") == "道德与法治"
    assert canonical("语文") == "语文"
    assert subject_bases("英语") == {"英语"}
    assert subject_bases("总分") == set()
    assert subject_bases("语文总分") == {"语文"}
    assert has_subject_word("期末数学") and not has_subject_word("班级排名")
    # 「道法」与「道德与法治」必须被判为同一门课（否则同一门课会被算两次）
    assert subject_bases("道法") & subject_bases("道德与法治")
    print("subjects.py 自检通过：%d 个学科词、%d 条同义映射"
          % (len(SUBJECT_POOL), len(SUBJECT_ALIAS)))
