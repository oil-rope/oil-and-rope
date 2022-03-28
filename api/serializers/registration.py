from django.apps import apps
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from common.constants import models

Profile = apps.get_model(models.PROFILE_MODEL)
User = apps.get_model(models.USER_MODEL)


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
