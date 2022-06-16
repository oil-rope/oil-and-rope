from rest_framework.routers import SimpleRouter

from ..viewsets.roleplay import DomainViewSet, PlaceViewSet, RaceViewSet

router = SimpleRouter()
router.register(prefix=r'domain', viewset=DomainViewSet, basename='domain')
router.register(prefix=r'place', viewset=PlaceViewSet, basename='place')
router.register(prefix=r'race', viewset=RaceViewSet, basename='race')

urls = router.urls
