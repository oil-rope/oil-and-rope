from rest_framework.routers import SimpleRouter

from ..viewsets.roleplay import CampaignViewSet, PlaceNestedViewSet

router = SimpleRouter()
router.register(r'campaign', viewset=CampaignViewSet)
router.register(r'place', viewset=PlaceNestedViewSet)

urls = router.urls
