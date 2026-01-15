# Copyright (c) 2026, Your Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, validate_email_address


class BlogComment(Document):
    """Blog Comment DocType for storing comments on blog posts."""

    def before_insert(self):
        """Set default values before insert."""
        # Ensure status is Pending for new comments
        self.status = "Pending"
        
        # Set created_at if not set
        if not self.created_at:
            self.created_at = now_datetime()

    def validate(self):
        """Validate comment data."""
        self.validate_required_fields()
        self.validate_email()
        self.validate_post_exists()

    def validate_required_fields(self):
        """Validate that required fields are not empty or whitespace only."""
        if not self.nickname or not self.nickname.strip():
            frappe.throw(_("Nickname cannot be empty"))
        
        if not self.email or not self.email.strip():
            frappe.throw(_("Email cannot be empty"))
        
        if not self.content or not self.content.strip():
            frappe.throw(_("Comment content cannot be empty"))

    def validate_email(self):
        """Validate email format."""
        if self.email:
            validate_email_address(self.email, throw=True)

    def validate_post_exists(self):
        """Validate that the linked post exists and is published."""
        if self.post:
            post_status = frappe.db.get_value("Blog Post", self.post, "status")
            if not post_status:
                frappe.throw(_("The linked blog post does not exist"))
            if post_status != "Published":
                frappe.throw(_("Comments can only be added to published posts"))

    def approve(self):
        """Approve the comment."""
        self.status = "Approved"
        self.save()
        return self

    def reject(self):
        """Reject the comment."""
        self.status = "Rejected"
        self.save()
        return self
