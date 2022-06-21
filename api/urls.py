from django.urls import include, path
from drf_spectacular.utils import extend_schema, extend_schema_view
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.authtoken.views import ObtainAuthToken

from .routers import chat, registration, roleplay
from .viewsets import api

app_name = 'api'

UTILS_PATTERNS = [
    path('resolver/', api.URLResolverView.as_view(), name='resolver'),
    path('roll/', api.RollView.as_view(), name='roll_dice'),
]

obtain_token_view = extend_schema_view(
    post=extend_schema(
        summary='Get token',
        description='Get token for given username and password.',
    ),
)(ObtainAuthToken.as_view())
AUTH_PATTERNS = [
    path('token/', obtain_token_view, name='token'),
]

urlpatterns = [
    path('', api.ApiVersionView.as_view(), name='version'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='api:schema'), name='swagger'),
    path('redoc/', SpectacularRedocView.as_view(url_name='api:schema'), name='redoc'),
    path('auth/', include((AUTH_PATTERNS, 'auth'))),
    path('utils/', include((UTILS_PATTERNS, 'utils'))),
    path('registration/', include((registration.urls, 'registration'))),
    path('chat/', include((chat.urls, 'chat'))),
    path('roleplay/', include((roleplay.urls, 'roleplay'))),
]
