from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsAdminUser(permissions.BasePermission):
    """
    Allow access only to admin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsDeveloper(permissions.BasePermission):
    """
    Allow access only to developer users (non-admin).
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and not request.user.is_staff
