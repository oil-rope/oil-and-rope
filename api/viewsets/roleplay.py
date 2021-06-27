from django.apps import apps
from rest_framework import permissions, viewsets
from rest_framework.settings import api_settings

from common.constants import models

from ..permissions import common
from ..serializers.roleplay import DomainSerializer, PlaceSerializer

Domain = apps.get_model(models.DOMAIN_MODEL)
Place = apps.get_model(models.PLACE_MODEL)


class DomainViewSet(viewsets.ModelViewSet):
    serializer_class = DomainSerializer
    queryset = Domain.objects.all()
    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES


class PlaceViewSet(viewsets.ModelViewSet):
    serializer_class = PlaceSerializer
    queryset = Place.objects.all()
    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES + [common.IsOwnerOrStaff]

    def get_permissions(self):
        if self.action == 'update':
            self.permission_classes = [permissions.IsAdminUser]
        return super().get_permissions()

    def get_serializer(self, *args, **kwargs):
        if 'data' not in kwargs:
            return super().get_serializer()

        data = kwargs['data']

        if self.action == 'partial_update':
            if 'owner' in data:
                del data['owner']
            if 'user' in data:
                del data['user']

        return super().get_serializer(*args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if not user.is_staff:
            qs = qs.filter(
                owner=user,
            )

        return qs
