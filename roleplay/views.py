from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from . import models


class WorldListView(LoginRequiredMixin, ListView):
    model = models.Place
    template_name = 'roleplay/world_list.html'

    def get_queryset(self):
        return super().get_queryset().filter(site_type=self.model.WORLD)

    def get_user_worlds(self):
        user = self.request.user
        return self.get_queryset().filter(user_id=user.id)

    def get_community_worlds(self):
        return self.get_queryset().filter(user__isnull=True)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()

        context['user_worlds'] = self.get_user_worlds()
        context['place_list'] = self.get_community_worlds()
        context['object_list'] = self.get_community_worlds()

        return context
