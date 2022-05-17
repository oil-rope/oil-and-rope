from django.urls import include, path

from . import views

app_name = 'roleplay'

PLACE_PATTERNS = [
    path('<int:pk>/', views.PlaceDetailView.as_view(), name='detail'),
    path('create/<int:pk>/', views.PlaceCreateView.as_view(), name='create'),
    path('edit/<int:pk>/', views.PlaceUpdateView.as_view(), name='edit'),
    path('delete/<int:pk>/', views.PlaceDeleteView.as_view(), name='delete'),
]

WORLD_PATTERNS = [
    path('', views.WorldListView.as_view(), name='list'),
    path('create/', views.WorldCreateView.as_view(), name='create'),
    path('edit/<int:pk>/', views.WorldUpdateView.as_view(), name='edit'),
]

CAMPAIGN_PATTERNS = [
    path('@me/', views.CampaignPrivateListView.as_view(), name='list-private'),
    path('<int:pk>/', views.CampaignDetailView.as_view(), name='detail'),
    path('create/<int:world_pk>/', views.CampaignCreateView.as_view(), name='create'),
    path('<int:pk>/<str:token>/', views.CampaignJoinView.as_view(), name='join'),
    path('edit/<int:pk>/', views.CampaignUpdateView.as_view(), name='edit'),
    path('delete/<int:pk>/', views.CampaignDeleteView.as_view(), name='delete'),
]

SESSION_PATTERNS = [
    path('', views.SessionListView.as_view(), name='list'),
    path('<int:pk>/', views.SessionDetailView.as_view(), name='detail'),
    path('create/<int:pk>/', views.SessionCreateView.as_view(), name='create'),
    path('edit/<int:pk>/', views.SessionUpdateView.as_view(), name='edit'),
    path('delete/<int:pk>/', views.SessionDeleteView.as_view(), name='delete'),
]

urlpatterns = [
    path('place/', include((PLACE_PATTERNS, 'place'))),
    path('world/', include((WORLD_PATTERNS, 'world'))),
    path('campaign/', include((CAMPAIGN_PATTERNS, 'campaign'))),
    path('session/', include((SESSION_PATTERNS, 'session'))),
]
