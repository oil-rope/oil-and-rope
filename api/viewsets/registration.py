from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings

from common.constants import models

from ..permissions.registration import IsUserOrAdmin, IsUserProfileOrAdmin
from ..serializers.registration import BotSerializer, ProfileSerializer, UserSerializer

Profile = apps.get_model(models.PROFILE_MODEL)
User = get_user_model()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for :class:`User`.
    """

    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES + [IsUserOrAdmin]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def get_object(self):
        if self.kwargs[self.lookup_url_kwarg or self.lookup_field] == '@me':
            return self.request.user
        return super().get_object()


class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for :class:`Profile`.
    """

    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES + [IsUserProfileOrAdmin]
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def get_object(self):
        if self.kwargs[self.lookup_url_kwarg or self.lookup_field] == '@me':
            return self.request.user.profile
        return super().get_object()


class BotViewSet(viewsets.ViewSet):
    """
    ViewSet for Oil & Rope Bot.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = BotSerializer

    def list(self, request):
        bot = User.objects.get(email=settings.DEFAULT_FROM_EMAIL)
        serializer = BotSerializer(bot)
        return Response(data=serializer.data)
