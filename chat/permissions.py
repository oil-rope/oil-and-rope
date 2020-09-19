from rest_framework import permissions


class UserInChat(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_staff:
            return True

        chat_users_pk = obj.users.values_list('pk', flat=True)

        return user.pk in chat_users_pk
