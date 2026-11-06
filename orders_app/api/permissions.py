from rest_framework import permissions


class IsCustomerUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        profile = getattr(request.user, 'profile', None)
        return bool(profile and profile.type == 'customer')


class IsOrderBusinessPartnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return bool(request.user and request.user.is_staff)
        if request.method == 'PATCH':
            profile = getattr(request.user, 'profile', None)
            return bool(profile and profile.type == 'business' and obj.business_user == request.user)
        return False