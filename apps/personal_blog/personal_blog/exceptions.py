"""
Personal Blog Custom Exceptions
自定义异常类，用于统一错误处理
"""

import frappe
from frappe import _


class BlogValidationError(frappe.ValidationError):
    """博客数据验证错误"""
    http_status_code = 400
    
    def __init__(self, message=None, errors=None):
        self.message = message or _("验证错误")
        self.errors = errors or []
        super().__init__(self.message)
    
    def as_dict(self):
        return {
            "exc_type": "BlogValidationError",
            "message": self.message,
            "errors": self.errors
        }


class BlogNotFoundError(frappe.DoesNotExistError):
    """博客资源不存在"""
    http_status_code = 404
    
    def __init__(self, message=None, resource_type=None, resource_id=None):
        self.message = message or _("资源不存在")
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(self.message)
    
    def as_dict(self):
        return {
            "exc_type": "BlogNotFoundError",
            "message": self.message,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id
        }


class BlogPermissionError(frappe.PermissionError):
    """博客权限错误"""
    http_status_code = 403
    
    def __init__(self, message=None, action=None):
        self.message = message or _("权限不足")
        self.action = action
        super().__init__(self.message)
    
    def as_dict(self):
        return {
            "exc_type": "BlogPermissionError",
            "message": self.message,
            "action": self.action
        }


def validate_required_fields(data, required_fields):
    """
    验证必填字段
    
    Args:
        data: 数据字典
        required_fields: 必填字段列表，格式为 [(field_name, display_name), ...]
    
    Raises:
        BlogValidationError: 如果有必填字段为空
    """
    errors = []
    for field_name, display_name in required_fields:
        value = data.get(field_name)
        if value is None or (isinstance(value, str) and not value.strip()):
            errors.append({
                "field": field_name,
                "message": _("{0} 不能为空").format(display_name)
            })
    
    if errors:
        raise BlogValidationError(
            message=_("请填写所有必填字段"),
            errors=errors
        )


def validate_email_format(email):
    """
    验证邮箱格式
    
    Args:
        email: 邮箱地址
    
    Raises:
        BlogValidationError: 如果邮箱格式无效
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise BlogValidationError(
            message=_("邮箱格式无效"),
            errors=[{
                "field": "email",
                "message": _("请输入有效的邮箱地址")
            }]
        )
