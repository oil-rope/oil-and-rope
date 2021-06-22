from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.settings import api_settings

from . import models, serializers


class PlaceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for :class:`Place`.
    """

    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES + [DjangoModelPermissions]
    queryset = models.Place.objects.all()
    serializer_class = serializers.PlaceSerializer
