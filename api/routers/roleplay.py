from django.urls import path

from ..viewsets.roleplay import DomainViewSet, PlaceViewSet, RaceViewSet, SessionViewSet
from .routers import OilAndRopeDefaultRouter

router = OilAndRopeDefaultRouter()
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

EXTRA_SESSION_PATTERNS = [
    path('session/@me', SessionViewSet.as_view({'get': 'user_list'}), name='session-user-list'),
    path('session/<int:pk>/invite', SessionViewSet.as_view({
        'post': 'invite_players_to_session'
    }), name='session-invite'),
]

urls = router.urls + EXTRA_PLACE_PATTERNS + EXTRA_RACE_PATTERNS + EXTRA_SESSION_PATTERNS
