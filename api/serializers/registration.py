from django.apps import apps
from django.contrib.auth import get_user_model
from rest_framework import serializers

from common.constants import models

Profile = apps.get_model(models.PROFILE_MODEL)


class UserSerializer(serializers.ModelSerializer):
    """
    API serializer for :class:`User`.
    """

    class Meta:
        model = get_user_model()
        exclude = ['password', 'groups', 'user_permissions']


class ProfileSerializer(serializers.ModelSerializer):
    """
    API serializer for :class:`Profile`.
    """

    user = UserSerializer()

    class Meta:
        model = Profile
        exclude = ['entry_created_at', 'entry_updated_at']
