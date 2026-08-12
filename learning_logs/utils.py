"""学习笔记的工具函数：根据主题名称自动生成 URL 别名（汉字转拼音）。"""
import re

from pypinyin import lazy_pinyin

# 主题名称允许的字符：汉字（含扩展区）、大小写字母、数字、连词符(-)、空格
_ALLOWED_CHARS_RE = re.compile(r'^[\u4e00-\u9fff\u3400-\u4dbfA-Za-z0-9\- ]+$')


def validate_topic_text(text):
    """校验主题名称是否符合要求（非空，且只包含允许的字符）。

    允许：汉字、大小写字母、数字、连词符(-)、空格。
    """
    if not text:
        return False
    return bool(_ALLOWED_CHARS_RE.fullmatch(text))


def slugify_pinyin(text):
    """根据主题名称自动生成 URL 别名。

    规则：
    - 汉字 → 拼音（直接拼接，不带声调，如：编程 → biancheng）
    - 空格 → 连词符（-）
    - 字母、数字、连词符原样保留
    - 整体转为小写，合并连续的连词符，去掉首尾连词符
    """
    parts = []
    for ch in text:
        if ch == ' ':
            parts.append('-')
        elif '\u4e00' <= ch <= '\u9fff' or '\u3400' <= ch <= '\u4dbf':
            parts.append(lazy_pinyin(ch)[0])
        else:
            parts.append(ch)

    slug = ''.join(parts)
    slug = re.sub(r'-+', '-', slug).strip('-').lower()
    return slug
