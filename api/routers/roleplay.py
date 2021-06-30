from django.urls import path

from ..viewsets.roleplay import DomainViewSet, PlaceViewSet, RaceViewSet
from .routers import OilAndRopeDefaultRouter

router = OilAndRopeDefaultRouter()
router.register(prefix=r'domain', viewset=DomainViewSet, basename='domain')
router.register(prefix=r'place', viewset=PlaceViewSet, basename='place')
router.register(prefix=r'race', viewset=RaceViewSet, basename='race')

EXTRA_PLACE_PATTERNS = [
    path('place/@me', PlaceViewSet.as_view({'get': 'user_list'}), name='place-user-list'),
]

EXTRA_RACE_PATTERNS = [
    path('race/@me', RaceViewSet.as_view({'get': 'user_list'}), name='race-user-list'),
]

urls = router.urls + EXTRA_PLACE_PATTERNS + EXTRA_RACE_PATTERNS
