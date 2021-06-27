from django.apps import apps
from rest_framework import serializers

from common.constants import models

Domain = apps.get_model(models.DOMAIN_MODEL)
Place = apps.get_model(models.PLACE_MODEL)


class DomainSerializer(serializers.ModelSerializer):

    class Meta:
        model = Domain
        fields = (
            'id', 'name', 'description', 'domain_type', 'image', 'entry_created_at', 'entry_updated_at',
        )


class PlaceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Place
        fields = (
            'id', 'name', 'description', 'site_type', 'image', 'parent_site', 'user', 'owner', 'entry_created_at',
            'entry_updated_at',
        )
