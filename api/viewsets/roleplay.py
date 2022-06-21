from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets

from roleplay.models import Campaign

from ..serializers.roleplay import CampaignSerializer


@extend_schema_view(
    list=extend_schema(summary='List campaigns', description='Returns a list of campaigns where user is a member.'),
    retrieve=extend_schema(summary='Get campaign', description='Returns a campaign by give ID.'),
)
class CampaignViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer

    def get_queryset(self) -> QuerySet:
        qs: QuerySet = super().get_queryset()
        return qs.filter(
            users__in=[self.request.user],
        )
