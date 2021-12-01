from rest_framework import permissions


class IsUserProfileOrAdmin(permissions.BasePermission):
    """
    Checks if :class:`auth.User` is the owner of the object.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        """
        Checks if owner is the same as `request.user`.
        """

        user = request.user
        if not user:
            return False
        if user.is_staff:
            return True
        return obj.user == request.user


class IsUserOrAdmin(permissions.BasePermission):
    """
    Checks if user is the one retrieving object.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        if not user:
            return False
        if user.is_staff:
            return True
        return obj == user
