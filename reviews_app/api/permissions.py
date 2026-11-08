from rest_framework import permissions


class IsCustomerUser(permissions.BasePermission):
    """Allow access only to authenticated users with a 'customer' profile."""

    def has_permission(self, request, view):
        """Return True if user is authenticated and has profile type 'customer'."""
        if not request.user or not request.user.is_authenticated:
            return False
        profile = getattr(request.user, 'profile', None)
        return bool(profile and profile.type == 'customer')


class IsReviewOwnerOrReadOnly(permissions.BasePermission):
    """Allow read access to any user, write/delete access only to the reviewer."""

    def has_object_permission(self, request, view, obj):
        """Return True for safe methods or if request.user wrote the review."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.reviewer == request.user