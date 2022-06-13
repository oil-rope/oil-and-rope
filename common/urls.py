from django.urls import include, path, re_path

from . import views

app_name = 'common'

UTILS_PATTERNS = [
    path('get_url/', views.ResolverView.as_view(), name='get_url'),
    re_path(r'^vote/(?P<model>\w+\.\w+)/(?P<pk>\d+)/', views.VoteView.as_view(), name='vote'),
]

urlpatterns = [
    path('utils/', include((UTILS_PATTERNS, 'utils'))),
]
