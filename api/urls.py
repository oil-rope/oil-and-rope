from django.urls import include, path

from .routers import registration
from . import views

app_name = 'api'

urlpatterns = [
    path('', views.ApiVersionView.as_view(), name='api:version'),
    path('registration/', include((registration.router.urls, 'registration'))),
]
