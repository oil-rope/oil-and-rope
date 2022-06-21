from rest_framework import serializers

from bot.models import Channel
from roleplay.models import Campaign, Domain, Place, Race


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


class CampaignSerializer(serializers.ModelSerializer):
    discord_channel = serializers.SerializerMethodField()

    def get_discord_channel(self, obj) -> str | None:
        discord_channel: Channel | None = obj.discord_channel
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
