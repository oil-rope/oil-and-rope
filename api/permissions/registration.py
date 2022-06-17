from rest_framework import permissions


class IsUserOrAdmin(permissions.BasePermission):
    """
    Checks if user (:class:`~registration.models.User`) is the one retrieving object or is admin.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        """
        Checks if `object` is user (:class:`registration.models.User`).
        """

        user = request.user
        if not user:
            return False
        if user.is_staff:
            return True
        return obj == user
