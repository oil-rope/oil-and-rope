from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from . import models, permissions, serializers


class ChatViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Chat.objects.all()
    serializer_class = serializers.ChatSerializer
    permission_classes = [permissions.UserInChat]

    def list(self, request, *args, **kwargs):
        user = request.user
        if not user.is_staff:
            raise PermissionDenied()

        return super().list(request, *args, **kwargs)
