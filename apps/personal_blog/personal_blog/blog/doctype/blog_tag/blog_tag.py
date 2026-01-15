# Copyright (c) 2026, Your Name and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from personal_blog.utils.slug import generate_slug


class BlogTag(Document):
    """Blog Tag DocType for tagging blog posts."""

    def before_save(self):
        """Generate slug before saving."""
        self.generate_slug()

    def generate_slug(self):
        """Auto-generate URL-friendly slug from tag name."""
        if not self.slug or self.has_value_changed("tag_name"):
            self.slug = generate_slug(
                self.tag_name,
                doctype="Blog Tag",
                existing_name=self.name if not self.is_new() else None
            )


def get_or_create_tag(tag_name: str) -> str:
    """
    Get existing tag or create a new one.
    
    Args:
        tag_name: Name of the tag
        
    Returns:
        Tag document name
    """
    tag_name = tag_name.strip()
    if not tag_name:
        return None
    
    # Check if tag exists
    existing = frappe.db.get_value("Blog Tag", {"tag_name": tag_name}, "name")
    if existing:
        return existing
    
    # Create new tag
    tag = frappe.get_doc({
        "doctype": "Blog Tag",
        "tag_name": tag_name
    })
    tag.insert(ignore_permissions=True)
    return tag.name
