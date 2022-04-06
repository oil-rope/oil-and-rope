from django.urls import path
from rest_framework.routers import SimpleRouter

from ..viewsets.roleplay import DomainViewSet, PlaceViewSet, RaceViewSet, SessionViewSet

router = SimpleRouter()
router.register(prefix=r'domain', viewset=DomainViewSet, basename='domain')
router.register(prefix=r'place', viewset=PlaceViewSet, basename='place')
router.register(prefix=r'race', viewset=RaceViewSet, basename='race')
router.register(prefix=r'session', viewset=SessionViewSet, basename='session')

EXTRA_PLACE_PATTERNS = [
    path('place/@me', PlaceViewSet.as_view({'get': 'user_list'}), name='place-user-list'),
]

EXTRA_RACE_PATTERNS = [
    path('race/@me', RaceViewSet.as_view({'get': 'user_list'}), name='race-user-list'),
]

urls = router.urls + EXTRA_PLACE_PATTERNS + EXTRA_RACE_PATTERNS
