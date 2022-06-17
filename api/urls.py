from django.conf import settings
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.authtoken.views import ObtainAuthToken

from .routers import chat, registration
from .viewsets import api

app_name = 'api'

UTILS_PATTERNS = [
    path('resolver/', api.URLResolverView.as_view(), name='resolver'),
    path('roll/', api.RollView.as_view(), name='roll_dice'),
]

AUTH_PATTERNS = [
    path('token/', ObtainAuthToken.as_view(), name='token'),
]

schema_view = get_schema_view(
    info=openapi.Info(
        title='Oil & Rope Project API',
        default_version=settings.REST_FRAMEWORK['DEFAULT_VERSION'],
    ),
    public=False,
)

urlpatterns = [
    path('', api.ApiVersionView.as_view(), name='version'),
    path('docs/', schema_view.with_ui('swagger'), name='swagger'),
    path('redoc/', schema_view.with_ui('redoc'), name='redoc'),
    path('auth/', include((AUTH_PATTERNS, 'auth'))),
    path('utils/', include((UTILS_PATTERNS, 'utils'))),
    path('registration/', include((registration.urls, 'registration'))),
    path('chat/', include((chat.urls, 'chat'))),
]
