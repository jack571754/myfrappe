"""Blog Tag API endpoints."""

import frappe
from frappe import _
from personal_blog.utils.slug import generate_slug


@frappe.whitelist(allow_guest=True, methods=["GET", "POST"], xss_safe=True)
def get_tags() -> list:
    """
    获取标签列表
    
    Returns:
        标签列表，包含每个标签的文章数量
    """
    tags = frappe.db.get_all(
        "Blog Tag",
        fields=["name", "tag_name", "slug"],
        order_by="tag_name asc"
    )
    
    # Add post count for each tag
    for tag in tags:
        tag["post_count"] = frappe.db.count(
            "Blog Post Tag",
            filters={"tag": tag["name"]}
        )
    
    return tags


@frappe.whitelist(allow_guest=True, methods=["GET", "POST"], xss_safe=True)
def get_tag(slug: str = None, name: str = None) -> dict:
    """
    获取标签详情
    
    Args:
        slug: 标签 slug
        name: 标签 ID
    
    Returns:
        标签详情
    """
    if not slug and not name:
        frappe.throw(_("Please provide either slug or name"), frappe.ValidationError)
    
    if slug:
        tag_name = frappe.db.get_value("Blog Tag", {"slug": slug}, "name")
        if not tag_name:
            frappe.throw(_("Tag not found"), frappe.DoesNotExistError)
    else:
        tag_name = name
        if not frappe.db.exists("Blog Tag", tag_name):
            frappe.throw(_("Tag not found"), frappe.DoesNotExistError)
    
    tag = frappe.get_doc("Blog Tag", tag_name)
    
    result = {
        "name": tag.name,
        "tag_name": tag.tag_name,
        "slug": tag.slug
    }
    
    # Add post count
    result["post_count"] = frappe.db.count(
        "Blog Post Tag",
        filters={"tag": tag.name}
    )
    
    return result


@frappe.whitelist()
def create_tag(tag_name: str) -> dict:
    """
    创建标签
    
    Args:
        tag_name: 标签名称
    
    Returns:
        创建的标签数据
    """
    if not tag_name or not tag_name.strip():
        frappe.throw(_("Tag name is required"), frappe.ValidationError)
    
    tag_name = tag_name.strip()
    
    # Check if tag already exists
    if frappe.db.exists("Blog Tag", tag_name):
        # Return existing tag
        return get_tag(name=tag_name)
    
    # Check by tag_name field
    existing = frappe.db.get_value("Blog Tag", {"tag_name": tag_name}, "name")
    if existing:
        return get_tag(name=existing)
    
    # Generate slug
    slug = generate_slug(tag_name, "Blog Tag")
    
    # Create tag
    tag = frappe.new_doc("Blog Tag")
    tag.tag_name = tag_name
    tag.slug = slug
    tag.insert()
    
    return get_tag(name=tag.name)


@frappe.whitelist()
def ensure_tag(tag_name: str) -> dict:
    """
    确保标签存在，如果不存在则自动创建
    
    这是标签自动创建逻辑的核心函数。
    
    Args:
        tag_name: 标签名称
    
    Returns:
        标签数据（已存在或新创建）
    """
    if not tag_name or not tag_name.strip():
        frappe.throw(_("Tag name is required"), frappe.ValidationError)
    
    tag_name = tag_name.strip()
    
    # Check if tag exists by name (primary key)
    if frappe.db.exists("Blog Tag", tag_name):
        return get_tag(name=tag_name)
    
    # Check by tag_name field
    existing = frappe.db.get_value("Blog Tag", {"tag_name": tag_name}, "name")
    if existing:
        return get_tag(name=existing)
    
    # Auto-create new tag
    slug = generate_slug(tag_name, "Blog Tag")
    
    tag = frappe.new_doc("Blog Tag")
    tag.tag_name = tag_name
    tag.slug = slug
    tag.insert(ignore_permissions=True)
    
    return get_tag(name=tag.name)


@frappe.whitelist()
def delete_tag(name: str) -> dict:
    """
    删除标签
    
    删除标签时，会自动移除所有文章与该标签的关联。
    
    Args:
        name: 标签 ID
    
    Returns:
        操作结果
    """
    if not frappe.db.exists("Blog Tag", name):
        frappe.throw(_("Tag not found"), frappe.DoesNotExistError)
    
    # Remove all associations with posts
    frappe.db.delete("Blog Post Tag", {"tag": name})
    
    # Delete the tag
    frappe.delete_doc("Blog Tag", name, force=True)
    
    return {
        "success": True,
        "message": _("Tag deleted successfully")
    }


@frappe.whitelist(allow_guest=True, methods=["GET", "POST"], xss_safe=True)
def get_popular_tags(limit: int = 10) -> list:
    """
    获取热门标签（按文章数量排序）
    
    Args:
        limit: 返回数量限制
    
    Returns:
        热门标签列表
    """
    limit = int(limit)
    
    # Get tags with post count
    tags = frappe.db.sql("""
        SELECT 
            t.name,
            t.tag_name,
            t.slug,
            COUNT(pt.name) as post_count
        FROM `tabBlog Tag` t
        LEFT JOIN `tabBlog Post Tag` pt ON pt.tag = t.name
        LEFT JOIN `tabBlog Post` p ON p.name = pt.parent AND p.status = 'Published'
        GROUP BY t.name, t.tag_name, t.slug
        HAVING post_count > 0
        ORDER BY post_count DESC
        LIMIT %s
    """, (limit,), as_dict=True)
    
    return tags
