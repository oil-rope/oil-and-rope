from rest_framework import permissions


class IsOwnerOrStaff(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        """
        Checks if user is owner of object or staff, otherwise returns False.
        """

        user = request.user

        if user.is_staff:
            return True

        return obj.owner == user
