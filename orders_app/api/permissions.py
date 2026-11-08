from rest_framework import permissions


class IsCustomerUser(permissions.BasePermission):
    """Allow access only to authenticated users with a 'customer' profile."""

    def has_permission(self, request, view):
        """Return True if user is authenticated and has profile type 'customer'."""
        if not request.user or not request.user.is_authenticated:
            return False
        profile = getattr(request.user, 'profile', None)
        return bool(profile and profile.type == 'customer')


class IsOrderBusinessPartnerOrAdmin(permissions.BasePermission):
    """Allow PATCH to order's business user and DELETE only to staff users."""

    def has_object_permission(self, request, view, obj):
        """Check staff status for DELETE and business ownership for PATCH."""
        if request.method == 'DELETE':
            return bool(request.user and request.user.is_staff)
        if request.method == 'PATCH':
            profile = getattr(request.user, 'profile', None)
            return bool(profile and profile.type == 'business' and obj.business_user == request.user)
        return False