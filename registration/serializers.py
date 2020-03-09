from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Profile


class UserSerializer(serializers.ModelSerializer):
    """
    API serializer for :class:`User`.
    """

    class Meta:
        model = User
        exclude = ['password', 'groups', 'user_permissions']


class ProfileSerializer(serializers.ModelSerializer):
    """
    API serializer for :class:`Profile`.
    """

    user = UserSerializer()

    class Meta:
        model = Profile
        exclude = ['entry_created_at', 'entry_updated_at']
