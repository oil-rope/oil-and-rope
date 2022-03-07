from rest_framework import permissions


class IsInPlayersOrStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        """
        Checks if user is staff or user in players.
        """

        user = request.user

        if user.is_staff:
            return True

        return user in obj.players.all()


class IsInGameMastersOrStaff(permissions.BasePermission):

    def has_object_permission(self, request, view, obj) -> bool:
        """
        Checks if user is staff or user in game masters.
        """

        user = request.user

        if user.is_staff:
            return True

        return user in obj.game_masters


class IsPublicOrStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user

        if user.is_staff:
            return True

        if not obj.user:
            return True

        return False
