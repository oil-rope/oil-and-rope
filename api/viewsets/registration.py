from django.apps import apps
from rest_framework import viewsets
from rest_framework.settings import api_settings

from common.constants import models

from ..permissions import IsUserOrAdmin, IsUserProfileOrAdmin
from ..serializers.registration import ProfileSerializer, UserSerializer
from .mixins import ListStaffRequiredMixin

Profile = apps.get_model(models.PROFILE_MODEL)
User = apps.get_model(models.USER_MODEL)


class UserViewSet(viewsets.ReadOnlyModelViewSet, ListStaffRequiredMixin):
    """
    ViewSet for :class:`User`.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES + [IsUserOrAdmin]


class ProfileViewSet(viewsets.ReadOnlyModelViewSet, ListStaffRequiredMixin):
    """
    ViewSet for :class:`Profile`.
    """

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES + [IsUserProfileOrAdmin]
