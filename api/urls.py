from django.urls import path, include
from .routers import registration

app_name = 'api'

urlpatterns = [
    path('registration/', include((registration.router.urls, 'registration'))),
]
