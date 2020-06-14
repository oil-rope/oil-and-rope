from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Profile


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
