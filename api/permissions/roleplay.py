from rest_framework import permissions


class IsPublicOrStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user

        if user.is_staff:
            return True

        if not obj.user:
            return True

        return False