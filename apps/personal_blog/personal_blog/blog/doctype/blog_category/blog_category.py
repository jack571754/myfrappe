# Copyright (c) 2026, Your Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from personal_blog.utils.slug import generate_slug


class BlogCategory(Document):
    """Blog Category DocType for organizing blog posts."""

    def before_save(self):
        """Generate slug before saving."""
        self.generate_slug()
        self.validate_category_name()

    def generate_slug(self):
        """Auto-generate URL-friendly slug from category name."""
        if not self.slug or self.has_value_changed("category_name"):
            self.slug = generate_slug(
                self.category_name,
                doctype="Blog Category",
                existing_name=self.name if not self.is_new() else None
            )

    def validate_category_name(self):
        """Validate that category name is not empty or whitespace only."""
        if not self.category_name or not self.category_name.strip():
            frappe.throw(_("Category name cannot be empty or contain only whitespace"))

    def before_insert(self):
        """Handle default category logic on insert."""
        if self.is_default:
            self.clear_other_defaults()

    def on_update(self):
        """Handle default category logic on update."""
        if self.is_default:
            self.clear_other_defaults()

    def clear_other_defaults(self):
        """Ensure only one default category exists."""
        frappe.db.sql(
            """
            UPDATE `tabBlog Category`
            SET is_default = 0
            WHERE name != %s AND is_default = 1
            """,
            self.name
        )

    def on_trash(self):
        """Move posts to default category before deletion."""
        default_category = get_default_category()
        
        if default_category and default_category != self.name:
            # Move all posts from this category to default
            frappe.db.sql(
                """
                UPDATE `tabBlog Post`
                SET category = %s
                WHERE category = %s
                """,
                (default_category, self.name)
            )
        elif self.is_default:
            frappe.throw(_("Cannot delete the default category"))


def get_default_category():
    """Get the default category name."""
    default = frappe.db.get_value("Blog Category", {"is_default": 1}, "name")
    if not default:
        # Return first category if no default is set
        default = frappe.db.get_value("Blog Category", {}, "name", order_by="creation")
    return default
