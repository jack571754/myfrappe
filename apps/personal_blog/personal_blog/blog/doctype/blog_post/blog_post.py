# Copyright (c) 2026, Your Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime

from personal_blog.utils.slug import generate_slug
from personal_blog.blog.doctype.blog_tag.blog_tag import get_or_create_tag


class BlogPost(Document):
    """Blog Post DocType for storing blog articles."""

    def before_save(self):
        """Generate slug and process content before saving."""
        self.generate_slug()
        self.process_content()

    def generate_slug(self):
        """Auto-generate URL-friendly slug from title."""
        if not self.slug or self.has_value_changed("title"):
            self.slug = generate_slug(
                self.title,
                doctype="Blog Post",
                existing_name=self.name if not self.is_new() else None
            )

    def process_content(self):
        """Process markdown content to HTML."""
        if self.content:
            # Store the rendered HTML content
            # Frappe's Text Editor already provides HTML, but we store it separately
            # for potential future markdown processing
            self.content_html = self.content

    def publish(self):
        """Publish the blog post."""
        if self.status == "Published":
            frappe.throw(_("Post is already published"))
        
        self.status = "Published"
        self.published_at = now_datetime()
        self.save()
        return self

    def unpublish(self):
        """Unpublish the blog post (move to draft)."""
        self.status = "Draft"
        self.save()
        return self

    def soft_delete(self):
        """Soft delete the blog post (move to trash)."""
        self.status = "Trash"
        self.save()
        return self

    def restore(self):
        """Restore a trashed blog post to draft."""
        if self.status != "Trash":
            frappe.throw(_("Only trashed posts can be restored"))
        
        self.status = "Draft"
        self.save()
        return self

    def increment_view_count(self):
        """Increment the view count for this post."""
        frappe.db.set_value(
            "Blog Post",
            self.name,
            "view_count",
            self.view_count + 1,
            update_modified=False
        )

    def set_tags(self, tag_names: list):
        """
        Set tags for this post, creating new tags if necessary.
        
        Args:
            tag_names: List of tag names to set
        """
        # Clear existing tags
        self.tags = []
        
        if not tag_names:
            return
        
        # Add new tags
        for tag_name in tag_names:
            if not tag_name or not tag_name.strip():
                continue
            
            # Get or create the tag
            tag_doc_name = get_or_create_tag(tag_name.strip())
            if tag_doc_name:
                self.append("tags", {"tag": tag_doc_name})

    def get_tag_names(self) -> list:
        """Get list of tag names for this post."""
        return [
            frappe.db.get_value("Blog Tag", row.tag, "tag_name")
            for row in self.tags
            if row.tag
        ]
