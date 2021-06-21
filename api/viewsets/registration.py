from django.apps import apps
from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.settings import api_settings

from common.constants import models

from ..permissions import IsUser, IsUserProfile
from ..serializers.registration import ProfileSerializer, UserSerializer
from .mixins import ListStaffRequiredMixin

Profile = apps.get_model(models.PROFILE_MODEL)


class UserViewSet(viewsets.ReadOnlyModelViewSet, ListStaffRequiredMixin):
    """
    ViewSet for :class:`User`.
    """

    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES + [IsUser]


class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for :class:`Profile`.
    """

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES + [IsUserProfile]
