"""Blog Category API endpoints."""

import frappe
from frappe import _
from personal_blog.utils.slug import generate_slug


@frappe.whitelist(allow_guest=True, methods=["GET", "POST"], xss_safe=True)
def get_categories() -> list:
    """
    获取分类列表
    
    Returns:
        分类列表，包含每个分类的文章数量
    """
    categories = frappe.db.get_all(
        "Blog Category",
        fields=["name", "category_name", "slug", "description", "is_default"],
        order_by="category_name asc"
    )
    
    # Add post count for each category
    for cat in categories:
        cat["post_count"] = frappe.db.count(
            "Blog Post",
            filters={
                "category": cat["name"],
                "status": "Published"
            }
        )
    
    return categories


@frappe.whitelist(allow_guest=True, methods=["GET", "POST"], xss_safe=True)
def get_category(slug: str = None, name: str = None) -> dict:
    """
    获取分类详情
    
    Args:
        slug: 分类 slug
        name: 分类 ID
    
    Returns:
        分类详情
    """
    if not slug and not name:
        frappe.throw(_("Please provide either slug or name"), frappe.ValidationError)
    
    if slug:
        category_name = frappe.db.get_value("Blog Category", {"slug": slug}, "name")
        if not category_name:
            frappe.throw(_("Category not found"), frappe.DoesNotExistError)
    else:
        category_name = name
        if not frappe.db.exists("Blog Category", category_name):
            frappe.throw(_("Category not found"), frappe.DoesNotExistError)
    
    category = frappe.get_doc("Blog Category", category_name)
    
    result = {
        "name": category.name,
        "category_name": category.category_name,
        "slug": category.slug,
        "description": category.description,
        "is_default": category.is_default
    }
    
    # Add post count
    result["post_count"] = frappe.db.count(
        "Blog Post",
        filters={
            "category": category.name,
            "status": "Published"
        }
    )
    
    return result


@frappe.whitelist()
def create_category(
    category_name: str,
    description: str = None,
    is_default: bool = False
) -> dict:
    """
    创建分类
    
    Args:
        category_name: 分类名称
        description: 分类描述
        is_default: 是否为默认分类
    
    Returns:
        创建的分类数据
    """
    if not category_name or not category_name.strip():
        frappe.throw(_("Category name is required"), frappe.ValidationError)
    
    category_name = category_name.strip()
    
    # Check if category already exists
    if frappe.db.exists("Blog Category", category_name):
        frappe.throw(_("Category already exists"), frappe.ValidationError)
    
    # Generate slug
    slug = generate_slug(category_name, "Blog Category")
    
    # If setting as default, unset other defaults
    if is_default:
        frappe.db.set_value(
            "Blog Category",
            {"is_default": 1},
            "is_default",
            0
        )
    
    # Create category
    category = frappe.new_doc("Blog Category")
    category.category_name = category_name
    category.slug = slug
    category.description = description
    category.is_default = is_default
    category.insert()
    
    return get_category(name=category.name)


@frappe.whitelist()
def update_category(name: str, **kwargs) -> dict:
    """
    更新分类
    
    Args:
        name: 分类 ID
        **kwargs: 要更新的字段
    
    Returns:
        更新后的分类数据
    """
    if not frappe.db.exists("Blog Category", name):
        frappe.throw(_("Category not found"), frappe.DoesNotExistError)
    
    category = frappe.get_doc("Blog Category", name)
    
    # Update allowed fields
    if "description" in kwargs:
        category.description = kwargs["description"]
    
    if "is_default" in kwargs and kwargs["is_default"]:
        # Unset other defaults
        frappe.db.set_value(
            "Blog Category",
            {"is_default": 1, "name": ["!=", name]},
            "is_default",
            0
        )
        category.is_default = 1
    
    # Note: category_name update would require rename which is complex
    # For now, we don't support renaming categories
    
    category.save()
    
    return get_category(name=category.name)


@frappe.whitelist()
def delete_category(name: str) -> dict:
    """
    删除分类
    
    删除分类时，将该分类下的所有文章移至默认分类。
    
    Args:
        name: 分类 ID
    
    Returns:
        操作结果
    """
    if not frappe.db.exists("Blog Category", name):
        frappe.throw(_("Category not found"), frappe.DoesNotExistError)
    
    category = frappe.get_doc("Blog Category", name)
    
    # Cannot delete default category
    if category.is_default:
        frappe.throw(_("Cannot delete the default category"), frappe.ValidationError)
    
    # Find default category
    default_category = frappe.db.get_value(
        "Blog Category",
        {"is_default": 1},
        "name"
    )
    
    if not default_category:
        # Create a default category if none exists
        default_cat = frappe.new_doc("Blog Category")
        default_cat.category_name = "Uncategorized"
        default_cat.slug = generate_slug("Uncategorized", "Blog Category")
        default_cat.is_default = 1
        default_cat.insert(ignore_permissions=True)
        default_category = default_cat.name
    
    # Move all posts from this category to default category
    posts_updated = frappe.db.sql("""
        UPDATE `tabBlog Post`
        SET category = %s
        WHERE category = %s
    """, (default_category, name))
    
    # Get count of affected posts
    affected_count = frappe.db.count(
        "Blog Post",
        filters={"category": default_category}
    )
    
    # Delete the category
    frappe.delete_doc("Blog Category", name, force=True)
    
    return {
        "success": True,
        "message": _("Category deleted successfully"),
        "posts_moved_to": default_category
    }


def get_default_category() -> str:
    """
    获取默认分类名称
    
    Returns:
        默认分类的 name
    """
    default_category = frappe.db.get_value(
        "Blog Category",
        {"is_default": 1},
        "name"
    )
    
    if not default_category:
        # Create default category if not exists
        if not frappe.db.exists("Blog Category", "Uncategorized"):
            category = frappe.new_doc("Blog Category")
            category.category_name = "Uncategorized"
            category.slug = generate_slug("Uncategorized", "Blog Category")
            category.is_default = 1
            category.insert(ignore_permissions=True)
            default_category = category.name
        else:
            default_category = "Uncategorized"
            frappe.db.set_value("Blog Category", "Uncategorized", "is_default", 1)
    
    return default_category
