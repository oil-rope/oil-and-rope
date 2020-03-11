from rest_framework import serializers

from .models import DiscordServer, DiscordTextChannel, DiscordUser, DiscordVoiceChannel


class DiscordUserSerializer(serializers.ModelSerializer):
    """
    API serializer for model :class:`DiscordUser`.
    """

    class Meta:
        model = DiscordUser
        exclude = ('code', 'entry_created_at', 'entry_updated_at')


class DiscordServerSerializer(serializers.ModelSerializer):
    """
    API serializer for model :class:`DiscordServer`.
    """

    class Meta:
        model = DiscordServer
        exclude = ('entry_created_at', 'entry_updated_at')


class DiscordTextChannelSerializer(serializers.ModelSerializer):
    """
    API serializer for model :class:`DiscordTextChannel`.
    """

    class Meta:
        model = DiscordTextChannel
        exclude = ('entry_created_at', 'entry_updated_at')


class DiscordVoiceChannelSerializer(serializers.ModelSerializer):
    """
    API serializer for model :class:`DiscordVoiceChannel`.
    """

    class Meta:
        model = DiscordVoiceChannel
        exclude = ('entry_created_at', 'entry_updated_at')
