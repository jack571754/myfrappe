"""Blog Post API endpoints."""

import frappe
from frappe import _
from personal_blog.utils.slug import generate_slug


@frappe.whitelist(allow_guest=True, methods=["GET", "POST"], xss_safe=True)
def get_posts(
    page: int = 1,
    page_size: int = 10,
    category: str = None,
    tag: str = None,
    status: str = "Published"
) -> dict:
    """
    获取文章列表
    
    Args:
        page: 页码，从 1 开始
        page_size: 每页数量
        category: 分类筛选 (slug 或 name)
        tag: 标签筛选 (slug 或 name)
        status: 状态筛选，默认只返回已发布
    
    Returns:
        {
            "posts": [...],
            "total": int,
            "page": int,
            "page_size": int
        }
    """
    page = int(page)
    page_size = int(page_size)
    
    # Build filters
    filters = {"status": status}
    
    if category:
        # Support both slug and name for category
        category_name = frappe.db.get_value(
            "Blog Category", 
            {"slug": category}, 
            "name"
        ) or category
        filters["category"] = category_name
    
    # Build query for tag filtering
    if tag:
        # Get tag name from slug if needed
        tag_name = frappe.db.get_value(
            "Blog Tag",
            {"slug": tag},
            "name"
        ) or tag
        
        # Get post names that have this tag
        post_names = frappe.db.get_all(
            "Blog Post Tag",
            filters={"tag": tag_name},
            pluck="parent"
        )
        
        if post_names:
            filters["name"] = ["in", post_names]
        else:
            # No posts with this tag
            return {
                "posts": [],
                "total": 0,
                "page": page,
                "page_size": page_size
            }
    
    # Get total count
    total = frappe.db.count("Blog Post", filters=filters)
    
    # Calculate offset
    offset = (page - 1) * page_size
    
    # Get posts
    posts = frappe.db.get_all(
        "Blog Post",
        filters=filters,
        fields=[
            "name", "title", "slug", "summary", "cover_image",
            "category", "status", "published_at", "author", "view_count"
        ],
        order_by="published_at desc, creation desc",
        start=offset,
        limit=page_size
    )
    
    # Enrich posts with tags and category info
    for post in posts:
        # Get tags
        post["tags"] = get_post_tags(post["name"])
        
        # Get category slug
        if post.get("category"):
            post["category_slug"] = frappe.db.get_value(
                "Blog Category",
                post["category"],
                "slug"
            )
    
    return {
        "posts": posts,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@frappe.whitelist(allow_guest=True, methods=["GET", "POST"], xss_safe=True)
def get_post(slug: str = None, name: str = None) -> dict:
    """
    获取文章详情
    
    Args:
        slug: 文章 slug
        name: 文章 ID
    
    Returns:
        文章完整数据
    """
    if not slug and not name:
        frappe.throw(_("Please provide either slug or name"), frappe.ValidationError)
    
    # Find post by slug or name
    if slug:
        post_name = frappe.db.get_value("Blog Post", {"slug": slug}, "name")
        if not post_name:
            frappe.throw(_("Post not found"), frappe.DoesNotExistError)
    else:
        post_name = name
        if not frappe.db.exists("Blog Post", post_name):
            frappe.throw(_("Post not found"), frappe.DoesNotExistError)
    
    # Get post document
    post = frappe.get_doc("Blog Post", post_name)
    
    # Build response
    result = {
        "name": post.name,
        "title": post.title,
        "slug": post.slug,
        "content": post.content,
        "content_html": post.content_html,
        "summary": post.summary,
        "cover_image": post.cover_image,
        "category": post.category,
        "status": post.status,
        "published_at": post.published_at,
        "author": post.author,
        "view_count": post.view_count,
        "tags": get_post_tags(post.name)
    }
    
    # Get category info
    if post.category:
        result["category_slug"] = frappe.db.get_value(
            "Blog Category",
            post.category,
            "slug"
        )
    
    # Get author info
    if post.author:
        result["author_name"] = frappe.db.get_value("User", post.author, "full_name")
        result["author_image"] = frappe.db.get_value("User", post.author, "user_image")
    
    return result


@frappe.whitelist()
def create_post(
    title: str,
    content: str,
    summary: str = None,
    cover_image: str = None,
    category: str = None,
    tags: list = None,
    status: str = "Draft"
) -> dict:
    """
    创建文章
    
    Args:
        title: 文章标题
        content: 文章内容 (Markdown)
        summary: 文章摘要
        cover_image: 封面图片
        category: 分类名称
        tags: 标签列表
        status: 状态，默认为草稿
    
    Returns:
        创建的文章数据
    """
    # Validate title
    if not title or not title.strip():
        frappe.throw(_("Title is required"), frappe.ValidationError)
    
    if not content or not content.strip():
        frappe.throw(_("Content is required"), frappe.ValidationError)
    
    # Generate slug
    slug = generate_slug(title, "Blog Post")
    
    # Create post document
    post = frappe.new_doc("Blog Post")
    post.title = title.strip()
    post.slug = slug
    post.content = content
    post.summary = summary.strip() if summary else None
    post.cover_image = cover_image
    post.category = category
    post.status = status
    
    # Handle tags
    if tags:
        if isinstance(tags, str):
            import json
            tags = json.loads(tags)
        
        for tag_name in tags:
            # Auto-create tag if not exists
            tag_doc_name = ensure_tag_exists(tag_name)
            post.append("tags", {"tag": tag_doc_name})
    
    post.insert()
    
    return get_post(name=post.name)


@frappe.whitelist()
def update_post(name: str, **kwargs) -> dict:
    """
    更新文章
    
    Args:
        name: 文章 ID
        **kwargs: 要更新的字段
    
    Returns:
        更新后的文章数据
    """
    if not frappe.db.exists("Blog Post", name):
        frappe.throw(_("Post not found"), frappe.DoesNotExistError)
    
    post = frappe.get_doc("Blog Post", name)
    
    # Update allowed fields
    allowed_fields = ["title", "content", "summary", "cover_image", "category"]
    
    for field in allowed_fields:
        if field in kwargs and kwargs[field] is not None:
            setattr(post, field, kwargs[field])
    
    # Regenerate slug if title changed
    if "title" in kwargs and kwargs["title"]:
        post.slug = generate_slug(kwargs["title"], "Blog Post", post.name)
    
    # Handle tags update
    if "tags" in kwargs:
        tags = kwargs["tags"]
        if isinstance(tags, str):
            import json
            tags = json.loads(tags)
        
        # Clear existing tags
        post.tags = []
        
        # Add new tags
        if tags:
            for tag_name in tags:
                tag_doc_name = ensure_tag_exists(tag_name)
                post.append("tags", {"tag": tag_doc_name})
    
    post.save()
    
    return get_post(name=post.name)


def get_post_tags(post_name: str) -> list:
    """Get list of tag names for a post."""
    tags = frappe.db.get_all(
        "Blog Post Tag",
        filters={"parent": post_name},
        fields=["tag"]
    )
    
    result = []
    for t in tags:
        tag_info = frappe.db.get_value(
            "Blog Tag",
            t["tag"],
            ["tag_name", "slug"],
            as_dict=True
        )
        if tag_info:
            result.append({
                "name": t["tag"],
                "tag_name": tag_info["tag_name"],
                "slug": tag_info["slug"]
            })
    
    return result


def ensure_tag_exists(tag_name: str) -> str:
    """
    Ensure a tag exists, create if not.
    
    Args:
        tag_name: Tag name
    
    Returns:
        Tag document name
    """
    # Check if tag exists
    if frappe.db.exists("Blog Tag", tag_name):
        return tag_name
    
    # Check by tag_name field
    existing = frappe.db.get_value("Blog Tag", {"tag_name": tag_name}, "name")
    if existing:
        return existing
    
    # Create new tag
    from personal_blog.utils.slug import generate_slug
    
    tag = frappe.new_doc("Blog Tag")
    tag.tag_name = tag_name
    tag.slug = generate_slug(tag_name, "Blog Tag")
    tag.insert(ignore_permissions=True)
    
    return tag.name



@frappe.whitelist()
def publish_post(name: str) -> dict:
    """
    发布文章
    
    将文章状态从 Draft 变更为 Published，并记录发布时间。
    
    Args:
        name: 文章 ID
    
    Returns:
        更新后的文章数据
    """
    if not frappe.db.exists("Blog Post", name):
        frappe.throw(_("Post not found"), frappe.DoesNotExistError)
    
    post = frappe.get_doc("Blog Post", name)
    
    if post.status == "Published":
        frappe.throw(_("Post is already published"), frappe.ValidationError)
    
    if post.status == "Trash":
        frappe.throw(_("Cannot publish a trashed post"), frappe.ValidationError)
    
    # Update status and published_at
    post.status = "Published"
    post.published_at = frappe.utils.now_datetime()
    post.save()
    
    return get_post(name=post.name)


@frappe.whitelist()
def delete_post(name: str) -> dict:
    """
    软删除文章（移至回收站）
    
    将文章状态变更为 Trash，而非永久删除。
    
    Args:
        name: 文章 ID
    
    Returns:
        操作结果
    """
    if not frappe.db.exists("Blog Post", name):
        frappe.throw(_("Post not found"), frappe.DoesNotExistError)
    
    post = frappe.get_doc("Blog Post", name)
    
    if post.status == "Trash":
        frappe.throw(_("Post is already in trash"), frappe.ValidationError)
    
    # Soft delete - change status to Trash
    post.status = "Trash"
    post.save()
    
    return {
        "success": True,
        "message": _("Post moved to trash"),
        "name": post.name
    }


@frappe.whitelist()
def restore_post(name: str) -> dict:
    """
    从回收站恢复文章
    
    将文章状态从 Trash 变更为 Draft。
    
    Args:
        name: 文章 ID
    
    Returns:
        更新后的文章数据
    """
    if not frappe.db.exists("Blog Post", name):
        frappe.throw(_("Post not found"), frappe.DoesNotExistError)
    
    post = frappe.get_doc("Blog Post", name)
    
    if post.status != "Trash":
        frappe.throw(_("Post is not in trash"), frappe.ValidationError)
    
    # Restore to Draft status
    post.status = "Draft"
    post.save()
    
    return get_post(name=post.name)
