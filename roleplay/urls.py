from django.urls import path, include

from . import views

app_name = 'roleplay'

PLACE_PATTERNS = [
    path('', views.WorldListView.as_view(), name='world_list'),
    path('create/', views.WorldCreateView.as_view(), name='world_create')
]

urlpatterns = [
    path('place/', include(PLACE_PATTERNS)),
]
