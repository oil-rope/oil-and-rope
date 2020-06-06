from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = 'core'

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='registration:login'), name='home'),
    path('index/', views.IndexView.as_view(), name='index')
]
