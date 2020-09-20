from django.urls import include, path

from . import views

app_name = 'dynamic_menu'

DYNAMIC_MENU_PATTERNS = [
    path('create/', views.DynamicMenuCreateView.as_view(), name='create'),
]

urlpatterns = [
    path('dynamic_menu/', include((DYNAMIC_MENU_PATTERNS, 'dynamic_menu'))),
]
