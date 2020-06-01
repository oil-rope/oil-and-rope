from rest_framework import viewsets

from . import models, serializers


class PlaceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for :class:`Place`.
    """

    queryset = models.Place.objects.all()
    serializer_class = serializers.PlaceSerializer
