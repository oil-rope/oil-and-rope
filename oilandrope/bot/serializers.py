from rest_framework import serializers

from .models import DiscordUser, DiscordServer, DiscordTextChannel, DiscordVoiceChannel


class DiscordUserSerializer(serializers.HyperlinkedModelSerializer):
    """
    API serializer for model :class:`DiscordUser`.
    """

    class Meta:
        model = DiscordUser
        fields = '__all__'


class DiscordServerSerializer(serializers.HyperlinkedModelSerializer):
    """
    API serializer for model :class:`DiscordServer`.
    """

    class Meta:
        model = DiscordServer
        fields = '__all__'


class DiscordTextChannelSerializer(serializers.HyperlinkedModelSerializer):
    """
    API serializer for model :class:`DiscordTextChannel`.
    """

    class Meta:
        model = DiscordTextChannel
        fields = '__all__'


class DiscordVoiceChannelSerializer(serializers.HyperlinkedModelSerializer):
    """
    API serializer for model :class:`DiscordVoiceChannel`.
    """

    class Meta:
        model = DiscordVoiceChannel
        fields = '__all__'
