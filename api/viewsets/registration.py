from django.apps import apps
from rest_framework import viewsets
from rest_framework.settings import api_settings

from common.constants import models

from ..permissions.registration import IsUserOrAdmin, IsUserProfileOrAdmin
from ..serializers.registration import ProfileSerializer, UserSerializer
from .mixins import ListStaffRequiredMixin

Profile = apps.get_model(models.PROFILE_MODEL)
User = apps.get_model(models.USER_MODEL)


class UserViewSet(viewsets.ReadOnlyModelViewSet, ListStaffRequiredMixin):
    """
    ViewSet for :class:`User`.
    """

    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES + [IsUserOrAdmin]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        if self.kwargs[self.lookup_url_kwarg or self.lookup_field] == '@me':
            return self.request.user
        return super().get_object()


class ProfileViewSet(viewsets.ReadOnlyModelViewSet, ListStaffRequiredMixin):
    """
    ViewSet for :class:`Profile`.
    """

    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES + [IsUserProfileOrAdmin]
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def get_object(self):
        if self.kwargs[self.lookup_url_kwarg or self.lookup_field] == '@me':
            return self.request.user.profile
        return super().get_object()
