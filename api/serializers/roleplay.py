from typing import Optional

from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers

from bot.models import Channel
from roleplay.managers import PlaceQuerySet
from roleplay.models import Campaign, Domain, Place, Race


class DomainSerializer(serializers.ModelSerializer):

    class Meta:
        model = Domain
        fields = (
            'id', 'name', 'description', 'domain_type', 'image', 'entry_created_at', 'entry_updated_at',
        )


@extend_schema_serializer(
    examples=[OpenApiExample(
        name='Example with nested children',
        value={
            'id': 1,
            'name': 'Planet Earth',
            'site_type': 17,
            'image': '',
            'parent_site': None,
            'owner': 1,
            'entry_created_at': '2020-01-01T08:00:00',
            'entry_updated_at': '2020-01-01T08:00:00',
            'children': [
                {
                    'id': 2,
                    'name': 'Europe',
                    'site_type': 16,
                    'image': '',
                    'parent_site': 1,
                    'owner': 1,
                    'entry_created_at': '2020-01-01T08:05:00',
                    'entry_updated_at': '2020-01-01T08:05:00',
                    'children': [],
                },
                {
                    'id': 3,
                    'name': 'America',
                    'site_type': 16,
                    'image': '',
                    'parent_site': 1,
                    'owner': 1,
                    'entry_created_at': '2020-01-01T08:11:00',
                    'entry_updated_at': '2020-01-01T08:11:00',
                    'children': [],
                }
            ],
        }
    )]
)
class PlaceNestedSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    def get_children(self, obj: Place):
        children: PlaceQuerySet = obj.get_children()
        if not children:
            return []
        serialized_children = PlaceNestedSerializer(children, many=True, read_only=True)
        return serialized_children.data

    class Meta:
        model = Place
        fields = (
            'id', 'name', 'description', 'site_type', 'image', 'parent_site', 'owner', 'entry_created_at',
            'entry_updated_at', 'children',
        )


class CampaignSerializer(serializers.ModelSerializer):
    discord_channel = serializers.SerializerMethodField()

    def get_discord_channel(self, obj) -> Optional[str]:
        discord_channel: Optional[Channel] = obj.discord_channel
        if discord_channel:
            return discord_channel.get_url()
        return discord_channel

    class Meta:
        model = Campaign
        fields = (
            'id', 'name', 'description', 'summary', 'cover_image', 'owner', 'users', 'place', 'start_date',
            'end_date', 'discord_channel', 'chat', 'entry_created_at', 'entry_updated_at',
        )


class RaceSerializer(serializers.ModelSerializer):

    owners = serializers.SerializerMethodField(method_name='get_owners')

    def get_owners(self, obj) -> list[int]:
        owners_pk = obj.owners.values_list('pk', flat=True)
        return list(owners_pk)

    class Meta:
        model = Race
        fields = (
            'id', 'name', 'description', 'strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma',
            'affected_by_armor', 'image', 'users', 'owners',
        )
