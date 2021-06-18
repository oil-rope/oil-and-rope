from rest_framework import permissions


class IsUserProfile(permissions.BasePermission):
    """
    Checks if :class:`auth.User` is the owner of the object.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        """
        Checks if owner is the same as `request.user`.
        """

        return obj.user == request.user


class IsUser(permissions.BasePermission):
    """
    Checks if user is the one retrieving object.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        return obj == request.user
