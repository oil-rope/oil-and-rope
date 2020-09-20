from django.urls import include, path

from . import views

app_name = 'common'

UTILS_PATTERNS = [
    path('get_url/', views.ResolverView.as_view(), name='get_url'),
]

urlpatterns = [
    path('utils/', include((UTILS_PATTERNS, 'utils'))),
]
