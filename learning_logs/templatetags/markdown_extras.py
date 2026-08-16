"""Markdown 渲染模板过滤器。

将 Entry.text 中保存的 Markdown 源码渲染为安全的 HTML：
1. python-markdown 负责语法解析（标题/列表/表格/代码块/任务列表等）
2. bleach 按白名单清理，防止 XSS（笔记详情页是公开可访问的）

用法：{% load markdown_extras %} 然后 {{ entry.text|markdown }}
"""
from django import template
from django.utils.safestring import mark_safe

import bleach
import markdown as md

register = template.Library()

# 允许的 HTML 标签（覆盖 Markdown 常见输出）
ALLOWED_TAGS = [
    'p', 'br', 'hr',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'strong', 'em', 'b', 'i', 'u', 's', 'del', 'ins',
    'mark', 'sub', 'sup', 'small',
    'blockquote', 'pre', 'code', 'kbd', 'samp',
    'ul', 'ol', 'li', 'dl', 'dt', 'dd',
    'a', 'img',
    'table', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td', 'caption',
    'details', 'summary',
    'input',  # 任务列表的复选框
    'abbr', 'dfn', 'cite', 'q', 'figure', 'figcaption',
]

# 允许的属性（class 保留给语法高亮 / 表格对齐等）
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
    'code': ['class'],
    'pre': ['class'],
    'th': ['colspan', 'rowspan', 'align'],
    'td': ['colspan', 'rowspan', 'align'],
    'input': ['type', 'checked', 'disabled'],
    'ol': ['start'],
    'abbr': ['title'],
    'q': ['cite'],
}

ALLOWED_PROTOCOLS = {'http', 'https', 'mailto', 'tel'}


@register.filter(name='markdown')
def markdown_to_html(value):
    """把 Markdown 文本渲染成经过白名单过滤的 HTML。"""
    if not value:
        return ''
    html = md.markdown(
        value,
        extensions=['extra', 'sane_lists', 'toc', 'nl2br'],
        output_format='html5',
    )
    clean = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )
    return mark_safe(clean)
