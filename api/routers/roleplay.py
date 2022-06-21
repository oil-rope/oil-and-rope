from rest_framework.routers import SimpleRouter

from ..viewsets.roleplay import CampaignViewSet

router = SimpleRouter()
router.register(r'campaign', viewset=CampaignViewSet)

urls = router.urls
