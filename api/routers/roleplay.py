from ..viewsets.roleplay import DomainViewSet, PlaceViewSet
from .routers import OilAndRopeDefaultRouter

router = OilAndRopeDefaultRouter()
router.register(prefix=r'domain', viewset=DomainViewSet, basename='domain')
router.register(prefix=f'place', viewset=PlaceViewSet, basename='place')
