from django.urls import include, path

from . import views

app_name = 'roleplay'

PLACE_PATTERNS = [
    path('create/<int:pk>/', views.PlaceCreateView.as_view(), name='create'),
    path('<int:pk>/', views.PlaceDetailView.as_view(), name='detail'),
]

WORLD_PATTERNS = [
    path('', views.WorldListView.as_view(), name='list'),
    path('create/', views.WorldCreateView.as_view(), name='create'),
    path('edit/<int:pk>/', views.WorldUpdateView.as_view(), name='edit'),
    path('delete/<int:pk>/', views.WorldDeleteView.as_view(), name='delete'),
]

SESSION_PATTERNS = [
    path('create/', views.SessionCreateView.as_view(), name='create'),
    path('<int:pk>/', views.SessionDetailView.as_view(), name='detail'),
    path('<int:pk>/join/', views.SessionJoinView.as_view(), name='join'),
]

urlpatterns = [
    path('place/', include((PLACE_PATTERNS, 'place'))),
    path('world/', include((WORLD_PATTERNS, 'world'))),
    path('session/', include((SESSION_PATTERNS, 'session'))),
]
