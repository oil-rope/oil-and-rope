from django.apps import apps
from rest_framework import serializers

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
            'user', 'bio', 'birthday', 'language', 'alias', 'web', 'image',
        )


class UserSerializer(serializers.ModelSerializer):
    """
    API serializer for :class:`User`.

    Parameter `auth_token` is taken as secure since nobody but admin and user itself can access this data.
    """

    profile = ProfileSerializer()

    def get_auth_token(self, obj):
        return obj.auth_token

    class Meta:
        model = User
        fields = (
            'id', 'last_login', 'username', 'first_name', 'last_name', 'is_active', 'date_joined', 'email',
            'is_premium', 'auth_token', 'profile',
        )
