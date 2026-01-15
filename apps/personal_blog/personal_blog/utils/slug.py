"""Slug generation utilities for blog posts and categories."""

import re
import frappe
from slugify import slugify


def generate_slug(title: str, doctype: str = "Blog Post", existing_name: str = None) -> str:
    """
    生成 URL 友好的 slug
    
    Args:
        title: 文章标题或分类名称
        doctype: DocType 名称，用于检查唯一性
        existing_name: 现有文档名称（更新时排除自身）
    
    Returns:
        唯一的 slug 字符串
    """
    if not title:
        return ""
    
    # 使用 python-slugify 生成基础 slug
    base_slug = slugify(title, allow_unicode=False, lowercase=True)
    
    if not base_slug:
        # 如果标题全是中文或特殊字符，使用拼音或时间戳
        import time
        base_slug = f"post-{int(time.time())}"
    
    slug = base_slug
    counter = 1
    
    # 检查唯一性
    while True:
        filters = {"slug": slug}
        if existing_name:
            filters["name"] = ["!=", existing_name]
        
        if not frappe.db.exists(doctype, filters):
            break
        
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    return slug


def is_valid_slug(slug: str) -> bool:
    """
    验证 slug 是否为 URL 友好格式
    
    Args:
        slug: 要验证的 slug 字符串
    
    Returns:
        True 如果 slug 格式有效
    """
    if not slug:
        return False
    
    # URL 友好的 slug: 小写字母、数字、连字符
    # 不能以连字符开头或结尾，不能有连续连字符
    pattern = r'^[a-z0-9]+(?:-[a-z0-9]+)*$'
    return bool(re.match(pattern, slug))
