from django.apps import apps
from rest_framework import serializers

from .chat import ChatSerializer
from common.constants import models
from .common import MappedSerializerMixin

Domain = apps.get_model(models.DOMAIN_MODEL)
Place = apps.get_model(models.PLACE_MODEL)
Race = apps.get_model(models.RACE_MODEL)
Session = apps.get_model(models.SESSION_MODEL)


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


class RaceSerializer(serializers.ModelSerializer):

    owners = serializers.SerializerMethodField(method_name='get_owners')

    def get_owners(self, obj):
        owners_pk = obj.owners.values_list('pk', flat=True)
        return list(owners_pk)

    class Meta:
        model = Race
        fields = (
            'id', 'name', 'description', 'strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma',
            'affected_by_armor', 'image', 'users', 'owners',
        )


class SessionSerializer(MappedSerializerMixin, serializers.ModelSerializer):
    serializers_map = {
        'chat': ChatSerializer(many=False, read_only=True)
    }

    game_masters = serializers.SerializerMethodField(method_name='get_game_masters')

    def get_game_masters(self, obj):
        gms_pk = obj.game_masters.values_list('pk', flat=True)
        return list(gms_pk)

    class Meta:
        model = Session
        fields = (
            'id', 'name', 'players', 'chat', 'next_game', 'system', 'world', 'game_masters',
        )
