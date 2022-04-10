from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from common.constants import models

Profile = apps.get_model(models.PROFILE_MODEL)
User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    """
    API serializer for :class:`Profile`.
    """

    class Meta:
        model = Profile
        fields = (
            'user', 'bio', 'birthday', 'language', 'web', 'image',
        )


class UserSerializer(serializers.ModelSerializer):
    """
    API serializer for :class:`User`.

    Parameter `auth_token` is taken as secure since nobody but admin and user itself can access this data.
    """

    profile = ProfileSerializer()
    token = serializers.SerializerMethodField()

    def get_token(self, obj):
        try:
            token_obj = Token.objects.get(user=obj)
        except Token.DoesNotExist:
            token_obj = Token.objects.create(user=obj)
        finally:
            return token_obj.key

    class Meta:
        model = User
        fields = (
            'id', 'last_login', 'username', 'first_name', 'last_name', 'is_active', 'date_joined', 'email',
            'is_premium', 'profile', 'token',
        )


class SimpleUserSerializer(serializers.ModelSerializer):
    """
    Simplified API serializer for :class:`User`.
    """

    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email',
        )


class BotSerializer(serializers.ModelSerializer):
    """
    API serializer for Oil & Rope bot.
    This serializer is quite simple and just includes: `id`, `username`, `email`, `command_prefix` and `description`.
    """

    command_prefix = serializers.SerializerMethodField(method_name='get_command_prefix')
    description = serializers.SerializerMethodField(method_name='get_description')

    def get_command_prefix(self, obj):
        return settings.BOT_COMMAND_PREFIX

    def get_description(self, obj):
        return settings.BOT_DESCRIPTION

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'command_prefix', 'description',
        )
