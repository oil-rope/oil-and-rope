from rest_framework import serializers

from .models import Place


class PlaceSerializer(serializers.ModelSerializer):

    user = serializers.HyperlinkedRelatedField(view_name='registration:api:user-detail', read_only=True)
    owner = serializers.HyperlinkedRelatedField(view_name='registration:api:user-detail', read_only=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = Place
        fields = ('id', 'name', 'description', 'site_type', 'parent_site', 'user', 'owner', 'children')

    def get_children(self, obj):
        children = obj.get_children()
        return PlaceSerializer(children, context=self.context, many=True).data
