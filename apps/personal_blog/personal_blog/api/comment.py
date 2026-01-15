"""Blog Comment API endpoints."""

import re
import frappe
from frappe import _
from personal_blog.exceptions import (
    BlogValidationError,
    BlogNotFoundError,
    validate_required_fields,
    validate_email_format
)


@frappe.whitelist(allow_guest=True)
def get_comments(post: str, page: int = 1, page_size: int = 20) -> dict:
    """
    获取文章评论列表（仅已审核）
    
    Args:
        post: 文章 ID 或 slug
        page: 页码，从 1 开始
        page_size: 每页数量
    
    Returns:
        {
            "comments": [...],
            "total": int,
            "page": int,
            "page_size": int
        }
    """
    page = int(page)
    page_size = int(page_size)
    
    # Resolve post name from slug if needed
    post_name = resolve_post_name(post)
    
    if not post_name:
        frappe.throw(_("Post not found"), frappe.DoesNotExistError)
    
    # Build filters - only approved comments
    filters = {
        "post": post_name,
        "status": "Approved"
    }
    
    # Get total count
    total = frappe.db.count("Blog Comment", filters=filters)
    
    # Calculate offset
    offset = (page - 1) * page_size
    
    # Get comments ordered by created_at ascending (oldest first)
    comments = frappe.db.get_all(
        "Blog Comment",
        filters=filters,
        fields=["name", "nickname", "content", "created_at"],
        order_by="created_at asc",
        start=offset,
        limit=page_size
    )
    
    return {
        "comments": comments,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@frappe.whitelist(allow_guest=True)
def submit_comment(
    post: str,
    nickname: str,
    email: str,
    content: str
) -> dict:
    """
    提交评论
    
    新评论默认状态为 Pending，需要审核后才会显示。
    
    Args:
        post: 文章 ID 或 slug
        nickname: 评论者昵称
        email: 评论者邮箱
        content: 评论内容
    
    Returns:
        提交的评论数据
    """
    # Validate required fields
    errors = []
    
    if not nickname or not nickname.strip():
        errors.append({
            "field": "nickname",
            "message": _("Nickname is required")
        })
    
    if not email or not email.strip():
        errors.append({
            "field": "email",
            "message": _("Email is required")
        })
    elif not is_valid_email(email):
        errors.append({
            "field": "email",
            "message": _("Invalid email format")
        })
    
    if not content or not content.strip():
        errors.append({
            "field": "content",
            "message": _("Content is required")
        })
    
    if errors:
        frappe.throw(
            _("Validation failed"),
            frappe.ValidationError,
            title=_("Invalid Input")
        )
    
    # Resolve post name
    post_name = resolve_post_name(post)
    
    if not post_name:
        frappe.throw(_("Post not found"), frappe.DoesNotExistError)
    
    # Check if post is published
    post_status = frappe.db.get_value("Blog Post", post_name, "status")
    if post_status != "Published":
        frappe.throw(_("Cannot comment on unpublished posts"), frappe.ValidationError)
    
    # Create comment with Pending status
    comment = frappe.new_doc("Blog Comment")
    comment.post = post_name
    comment.nickname = nickname.strip()
    comment.email = email.strip().lower()
    comment.content = content.strip()
    comment.status = "Pending"
    comment.created_at = frappe.utils.now_datetime()
    comment.insert(ignore_permissions=True)
    
    return {
        "success": True,
        "message": _("Comment submitted successfully and is pending approval"),
        "comment": {
            "name": comment.name,
            "nickname": comment.nickname,
            "content": comment.content,
            "status": comment.status,
            "created_at": comment.created_at
        }
    }


@frappe.whitelist()
def approve_comment(name: str) -> dict:
    """
    审核通过评论
    
    Args:
        name: 评论 ID
    
    Returns:
        更新后的评论数据
    """
    if not frappe.db.exists("Blog Comment", name):
        frappe.throw(_("Comment not found"), frappe.DoesNotExistError)
    
    comment = frappe.get_doc("Blog Comment", name)
    
    if comment.status == "Approved":
        frappe.throw(_("Comment is already approved"), frappe.ValidationError)
    
    comment.status = "Approved"
    comment.save()
    
    return {
        "success": True,
        "message": _("Comment approved"),
        "comment": {
            "name": comment.name,
            "nickname": comment.nickname,
            "content": comment.content,
            "status": comment.status,
            "created_at": comment.created_at
        }
    }


@frappe.whitelist()
def reject_comment(name: str) -> dict:
    """
    拒绝评论
    
    Args:
        name: 评论 ID
    
    Returns:
        更新后的评论数据
    """
    if not frappe.db.exists("Blog Comment", name):
        frappe.throw(_("Comment not found"), frappe.DoesNotExistError)
    
    comment = frappe.get_doc("Blog Comment", name)
    
    if comment.status == "Rejected":
        frappe.throw(_("Comment is already rejected"), frappe.ValidationError)
    
    comment.status = "Rejected"
    comment.save()
    
    return {
        "success": True,
        "message": _("Comment rejected"),
        "comment": {
            "name": comment.name,
            "nickname": comment.nickname,
            "content": comment.content,
            "status": comment.status,
            "created_at": comment.created_at
        }
    }


@frappe.whitelist()
def delete_comment(name: str) -> dict:
    """
    删除评论
    
    Args:
        name: 评论 ID
    
    Returns:
        操作结果
    """
    if not frappe.db.exists("Blog Comment", name):
        frappe.throw(_("Comment not found"), frappe.DoesNotExistError)
    
    frappe.delete_doc("Blog Comment", name, force=True)
    
    return {
        "success": True,
        "message": _("Comment deleted successfully")
    }


@frappe.whitelist()
def get_pending_comments(page: int = 1, page_size: int = 20) -> dict:
    """
    获取待审核评论列表（管理员用）
    
    Args:
        page: 页码
        page_size: 每页数量
    
    Returns:
        待审核评论列表
    """
    page = int(page)
    page_size = int(page_size)
    
    filters = {"status": "Pending"}
    
    total = frappe.db.count("Blog Comment", filters=filters)
    offset = (page - 1) * page_size
    
    comments = frappe.db.get_all(
        "Blog Comment",
        filters=filters,
        fields=["name", "post", "nickname", "email", "content", "created_at"],
        order_by="created_at desc",
        start=offset,
        limit=page_size
    )
    
    # Add post title for each comment
    for comment in comments:
        comment["post_title"] = frappe.db.get_value(
            "Blog Post",
            comment["post"],
            "title"
        )
    
    return {
        "comments": comments,
        "total": total,
        "page": page,
        "page_size": page_size
    }


def resolve_post_name(post_identifier: str) -> str:
    """
    解析文章标识符为文章名称
    
    Args:
        post_identifier: 文章 ID 或 slug
    
    Returns:
        文章名称，如果不存在则返回 None
    """
    # First try as direct name
    if frappe.db.exists("Blog Post", post_identifier):
        return post_identifier
    
    # Try as slug
    post_name = frappe.db.get_value("Blog Post", {"slug": post_identifier}, "name")
    return post_name


def is_valid_email(email: str) -> bool:
    """
    验证邮箱格式
    
    Args:
        email: 邮箱地址
    
    Returns:
        True 如果格式有效
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
