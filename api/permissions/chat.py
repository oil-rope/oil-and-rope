from rest_framework import permissions


class IsAuthor(permissions.BasePermission):
    """
    Checks if user (:class:`~registration.models.User`) is the one retrieving object.
    """

    def has_object_permission(self, request, view, obj):
        """
        Checks if :class:`~registration.models.User` is author of :class:`~chat.models.ChatMessage`.
        """

        user = request.user
        return obj.author == user
