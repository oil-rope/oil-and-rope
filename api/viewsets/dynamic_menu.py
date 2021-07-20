from django.apps import apps
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from common.constants import models

from ..serializers.dynamic_menu import DynamicMenuSerializer

DynamicMenu = apps.get_model(models.DYNAMIC_MENU)


class DynamicMenuViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = DynamicMenu.objects.all()
    serializer_class = DynamicMenuSerializer
