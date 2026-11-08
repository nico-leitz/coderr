from rest_framework import permissions


class IsProfileOwnerOrReadOnly(permissions.BasePermission):
    """Allow read access to authenticated users, write access only to profile owner."""

    def has_object_permission(self, request, view, obj):
        """Return True for safe methods or if the user owns the profile."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user