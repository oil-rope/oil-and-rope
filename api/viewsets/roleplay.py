from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, viewsets

from roleplay.managers import CampaignQuerySet, PlaceQuerySet
from roleplay.models import Campaign, Place

from ..serializers.roleplay import CampaignSerializer, PlaceNestedSerializer


@extend_schema_view(
    list=extend_schema(summary='List campaigns', description='Returns a list of campaigns where user is a member.'),
    retrieve=extend_schema(summary='Get campaign', description='Returns a campaign by give ID.'),
)
class CampaignViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer

    def get_queryset(self) -> CampaignQuerySet:
        qs: CampaignQuerySet = super().get_queryset()
        return qs.filter(
            users__in=[self.request.user],
        )


@extend_schema_view(
    retrieve=extend_schema(summary='Get place', description='Returns a place/world by given ID.'),
)
class PlaceNestedViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceNestedSerializer

    def get_queryset(self) -> PlaceQuerySet:
        qs: PlaceQuerySet = super().get_queryset()
        qs = qs.community_places() | Place.objects.filter(owner=self.request.user)
        return qs
