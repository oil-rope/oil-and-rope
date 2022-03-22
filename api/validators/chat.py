from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class UserInAuthorValidator:
    require_context = True

    def __init__(self, base):
        self.base = base

    def __call__(self, value, serializer_field):
        user = serializer_field.context['request'].user
        if value == user.pk:
            message = _('you can\'t set an author that is not yourself.').capitalize()
            raise serializers.ValidationError(message)
