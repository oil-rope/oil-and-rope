from django.apps import apps
from rest_framework import serializers

from common.constants import models

DynamicMenu = apps.get_model(models.DYNAMIC_MENU)


class DynamicMenuSerializer(serializers.ModelSerializer):
    models = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    def get_models(self, obj):
        return list(obj.models)

    def get_permissions(self, obj):
        return list(obj.permissions)

    class Meta:
        model = DynamicMenu
        fields = (
            'id', 'name', 'description', 'prepended_text', 'appended_text', 'url_resolver', 'extra_urls_args', 'order',
            'permissions', 'staff_required', 'superuser_required', 'icon', 'menu_type', 'models', 'entry_created_at',
            'entry_updated_at', 'parent',
        )
