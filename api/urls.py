from django.urls import include, path

from .routers import registration

app_name = 'api'

urlpatterns = [
    path('registration/', include((registration.router.urls, 'registration'))),
]
