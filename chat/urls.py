from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()


app_name = "chat"

urlpatterns = [
    path('api/', include(router.urls)),
]
