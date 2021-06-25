from django.apps import apps
from rest_framework import serializers

from common.constants import models

Domain = apps.get_model(models.DOMAIN_MODEL)


class DomainSerializer(serializers.ModelSerializer):

    class Meta:
        model = Domain
        fields = ('id', 'name', 'description', 'domain_type', 'image', 'entry_created_at', 'entry_updated_at')
