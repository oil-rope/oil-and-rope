from django.apps import apps
from rest_framework import permissions, viewsets
from rest_framework.settings import api_settings

from common.constants import models

from ..permissions import common
from ..serializers.roleplay import DomainSerializer, PlaceSerializer, RaceSerializer
from .mixins import UserListMixin

Domain = apps.get_model(models.DOMAIN_MODEL)
Place = apps.get_model(models.PLACE_MODEL)
Race = apps.get_model(models.RACE_MODEL)


# TODO: Disable creating Domain for non staff users
class DomainViewSet(viewsets.ModelViewSet):
    serializer_class = DomainSerializer
    queryset = Domain.objects.all()
    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES


class PlaceViewSet(UserListMixin, viewsets.ModelViewSet):
    related_name = 'places'
    serializer_class = PlaceSerializer
    queryset = Place.objects.all()
    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES + [common.IsOwnerOrStaff]

    def get_permissions(self):
        if self.action == 'update':
            self.permission_classes = [permissions.IsAdminUser]
        return super().get_permissions()

    def get_serializer(self, *args, **kwargs):
        if 'data' not in kwargs:
            return super().get_serializer(*args, **kwargs)

        user = self.request.user
        if user.is_staff:
            return super().get_serializer(*args, **kwargs)

        data = kwargs['data'].copy()

        if self.action == 'partial_update':
            if 'owner' in data:
                del data['owner']
            if 'user' in data:
                del data['user']

        if self.action == 'create':
            data.appendlist('owner', user.pk)
            if not data.get('public', False):
                data.appendlist('user', user.pk)

        kwargs['data'] = data
        return super().get_serializer(*args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()

        if self.action == 'list' and not user.is_staff:
            qs = Place.objects.community_places()

        return qs


class RaceViewSet(viewsets.ModelViewSet):
    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES
    queryset = Race.objects.all()
    serializer_class = RaceSerializer
