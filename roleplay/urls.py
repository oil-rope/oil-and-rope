from django.urls import include, path
from rest_framework import routers

from . import views, viewsets

router = routers.DefaultRouter()
router.register('place', viewsets.PlaceViewSet)

app_name = 'roleplay'

PLACE_PATTERNS = [
    path('', views.WorldListView.as_view(), name='world_list'),
    path('create/', views.WorldCreateView.as_view(), name='world_create'),
    path('<int:pk>/', views.WorldDetailView.as_view(), name='world_detail'),
    path('edit/<int:pk>/', views.WorldUpdateView.as_view(), name='world_edit'),
    path('delete/<int:pk>/', views.WorldDeleteView.as_view(), name='world_delete')
]

urlpatterns = [
    path('api/', include(router.urls)),
    path('place/', include(PLACE_PATTERNS)),
]
