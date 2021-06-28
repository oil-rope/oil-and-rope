from django.urls import path

from ..viewsets.roleplay import DomainViewSet, PlaceViewSet
from .routers import OilAndRopeDefaultRouter

router = OilAndRopeDefaultRouter()
router.register(prefix=r'domain', viewset=DomainViewSet, basename='domain')
router.register(prefix=r'place', viewset=PlaceViewSet, basename='place')

EXTRA_PLACE_PATTERNS = [
    path('place/@me', PlaceViewSet.as_view({'get': 'user_list'}), name='place-user-list'),
]

urls = router.urls + EXTRA_PLACE_PATTERNS
