from django.urls import path, include

from . import views

app_name = 'roleplay'

PLACE_PATTERNS = [
    path('', views.PlaceListView.as_view(), name='place_list'),
]

urlpatterns = [
    path('place/', include(PLACE_PATTERNS)),
]
