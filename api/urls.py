from django.urls import include, path

from . import views
from .routers import registration

app_name = 'api'

urlpatterns = [
    path('', views.ApiVersionView.as_view(), name='api:version'),
    path('registration/', include((registration.router.urls, 'registration'))),
]
