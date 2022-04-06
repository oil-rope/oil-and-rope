from django.apps import apps
from rest_framework import serializers

from common.constants import models

Chat = apps.get_model(models.CHAT_MODEL)
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
    children = serializers.SerializerMethodField()

    def get_children(self, obj):
        children = obj.get_children()
        if not children:
            return []
        serialized_children = PlaceSerializer(children, many=True, read_only=True)
        return serialized_children.data

    class Meta:
        model = Place
        fields = (
            'id', 'name', 'description', 'site_type', 'image', 'parent_site', 'user', 'owner', 'entry_created_at',
            'entry_updated_at', 'children',
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


class SessionSerializer(serializers.ModelSerializer):
    game_masters = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    def save(self, **kwargs):
        # NOTE: We create the chat on the go
        chat = Chat.objects.create(
            name=self.validated_data.get('name') + ' chat',
        )
        kwargs['chat'] = chat
        return super().save(**kwargs)

    class Meta:
        model = Session
        fields = (
            'id', 'name', 'plot', 'players', 'chat', 'next_game', 'system', 'world', 'game_masters',
        )
        extra_kwargs = {
            'chat': {'required': False},
        }
