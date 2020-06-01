from rest_framework import serializers

from .models import Place


class PlaceSerializer(serializers.ModelSerializer):

    user = serializers.HyperlinkedIdentityField(view_name='registration:user-detail')
    owner = serializers.HyperlinkedIdentityField(view_name='registration:user-detail')

    class Meta:
        model = Place
        fields = ('name', 'description', 'site_type', 'user', 'owner')
