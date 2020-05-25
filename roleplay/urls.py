from django.urls import include, path

from . import views

app_name = 'roleplay'

PLACE_PATTERNS = [
    path('', views.WorldListView.as_view(), name='world_list'),
    path('create/', views.WorldCreateView.as_view(), name='world_create'),
    path('<int:pk>/', views.WorldDetailView.as_view(), name='world_detail')
]

urlpatterns = [
    path('place/', include(PLACE_PATTERNS)),
]
