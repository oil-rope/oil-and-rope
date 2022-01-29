from rest_framework import permissions


class IsOwnerOrStaff(permissions.BasePermission):
    """
    Allow access only if user (:class:`~registration.models.User`) is object owner or staff.
    """

    def has_object_permission(self, request, view, obj):
        """
        Returns `True` if user is staff or object owner. Otherwise returns `False`.
        """

        user = request.user

        if user.is_staff:
            return True

        return obj.owner == user


class IsInOwnersOrStaff(permissions.BasePermission):
    """
    Same functionality as :class:`~.IsOwnerOrStaff` but checks on `owners` attribute since `object` is supposed to have
    multiple owners.
    """

    def has_object_permission(self, request, view, obj):
        """
        Checks if user is in owners or is staff, otherwise returns False.
        """

        user = request.user

        if user.is_staff:
            return True

        return user in obj.owners.all()
