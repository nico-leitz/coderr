from rest_framework import permissions


class IsBusinessUser(permissions.BasePermission):
    """Allow access only to authenticated users with a 'business' profile."""

    def has_permission(self, request, view):
        """Return True if user is authenticated and has profile type 'business'."""
        if not request.user or not request.user.is_authenticated:
            return False
        profile = getattr(request.user, 'profile', None)
        return bool(profile and profile.type == 'business')


class IsOfferOwnerOrReadOnly(permissions.BasePermission):
    """Allow read access to any user, write/delete access only to offer creator."""

    def has_object_permission(self, request, view, obj):
        """Return True for safe methods or if request.user created the offer."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user