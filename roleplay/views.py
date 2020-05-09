from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from . import models


class PlaceListView(LoginRequiredMixin, ListView):
    model = models.Place
    template_name = 'roleplay/place_list.html'
