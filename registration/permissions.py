from rest_framework import permissions


class IsModelOwner(permissions.BasePermission):
    """
    Checks if :class:`auth.User` is the owner of the object.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        """
        Checks if owner is the same as `request.user`.
        """

        return obj == request.user  # pragma: no cover
