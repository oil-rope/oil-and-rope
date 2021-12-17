from django.urls import include, path

from . import views

app_name = 'roleplay'

PATTERNS = [
    path('', views.WorldListView.as_view(), name='list'),
    path('create/', views.WorldCreateView.as_view(), name='create'),
    path('<int:pk>/', views.WorldDetailView.as_view(), name='detail'),
    path('edit/<int:pk>/', views.WorldUpdateView.as_view(), name='edit'),
    path('delete/<int:pk>/', views.WorldDeleteView.as_view(), name='delete'),
]

SESSION_PATTERNS = [
    path('create/', views.SessionCreateView.as_view(), name='create'),
    path('<int:pk>/', views.SessionDetailView.as_view(), name='detail'),
    path('<int:pk>/join/', views.SessionJoinView.as_view(), name='join'),
]

urlpatterns = [
    path('world/', include((PATTERNS, 'world'))),
    path('session/', include((SESSION_PATTERNS, 'session'))),
]
