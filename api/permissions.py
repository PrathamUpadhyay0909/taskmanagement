from rest_framework.permissions import BasePermission

def is_manager(user):
    return hasattr(user, "manager_profile")

def is_employee(user):
    return hasattr(user, "employee_profile")

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and is_manager(request.user)

class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and is_employee(request.user)
