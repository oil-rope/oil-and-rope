from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from . import models


class PlaceListView(LoginRequiredMixin, ListView):
    model = models.Place
    template_name = 'roleplay/place_list.html'

    def get_user_places(self):
        user = self.request.user
        return super().get_queryset().filter(user_id=user.id)

    def get_community_places(self):
        return super().get_queryset().filter(user__isnull=True)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()

        context['user_places'] = self.get_user_places()
        context['place_list'] = self.get_community_places()
        context['object_list'] = self.get_community_places()

        return context
