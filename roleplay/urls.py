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
    path('', views.CampaignListView.as_view(), name='list'),
    path('@me/', views.CampaignUserListView.as_view(), name='list-private'),
    path('<int:pk>/', views.CampaignDetailView.as_view(), name='detail'),
    path('create/<int:world_pk>/', views.CampaignCreateView.as_view(), name='create'),
    path('<int:pk>/leave/', views.CampaignLeaveView.as_view(), name='leave'),
    path('<int:pk>/remove/<int:user_pk>/', views.CampaignRemovePlayerView.as_view(), name='remove-player'),
    path('<int:pk>/<str:token>/', views.CampaignJoinView.as_view(), name='join'),
    path('edit/<int:pk>/', views.CampaignUpdateView.as_view(), name='edit'),
    path('delete/<int:pk>/', views.CampaignDeleteView.as_view(), name='delete'),
]

SESSION_PATTERNS = [
    path('', views.SessionListView.as_view(), name='list'),
    path('<int:pk>/', views.SessionDetailView.as_view(), name='detail'),
    path('create/<int:campaign_pk>/', views.SessionCreateView.as_view(), name='create'),
    path('edit/<int:pk>/', views.SessionUpdateView.as_view(), name='edit'),
    path('delete/<int:pk>/', views.SessionDeleteView.as_view(), name='delete'),
]

RACE_PATTERNS = [
    path('@me/', views.RaceListView.as_view(), name='list'),
    path('<int:pk>/', views.RaceDetailView.as_view(), name='detail'),
    path('create/place/', views.RaceCreateForPlaceView.as_view(), name='create-for-place'),
    path('create/place/<int:pk>/', views.RaceCreateForPlaceView.as_view(), name='create-for-place'),
    path('create/campaign/', views.RaceCreateForCampaignView.as_view(), name='create-for-campaign'),
    path('create/campaign/<int:pk>/', views.RaceCreateForCampaignView.as_view(), name='create-for-campaign'),
    path('edit/<int:pk>/', views.RaceUpdateView.as_view(), name='edit'),
    path('delete/<int:pk>/', views.RaceDeleteView.as_view(), name='delete'),
]

urlpatterns = [
    path('place/', include((PLACE_PATTERNS, 'place'))),
    path('world/', include((WORLD_PATTERNS, 'world'))),
    path('campaign/', include((CAMPAIGN_PATTERNS, 'campaign'))),
    path('session/', include((SESSION_PATTERNS, 'session'))),
    path('race/', include((RACE_PATTERNS, 'race'))),
]
