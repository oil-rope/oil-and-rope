import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.urls import reverse_lazy

from common.views import MultiplePaginatorListView
from . import models, forms

LOGGER = logging.getLogger(__name__)


class WorldListView(LoginRequiredMixin, MultiplePaginatorListView):
    model = models.Place
    paginate_by = 9
    user_worlds_page_kwarg = 'page_user_worlds'
    queryset = models.Place.objects.filter(site_type=models.Place.WORLD)
    template_name = 'roleplay/world_list.html'

    def get_user_worlds(self):
        user = self.request.user
        return self.get_queryset().filter(user_id=user.id)

    def get_community_worlds(self):
        return self.get_queryset().filter(user__isnull=True)

    def paginate_user_worlds(self, page_size):
        queryset = self.get_user_worlds()
        page_kwarg = self.user_worlds_page_kwarg
        return self.paginate_queryset_by_page_kwarg(queryset, page_size, page_kwarg)

    def paginate_community_worlds(self, page_size):
        queryset = self.get_community_worlds()
        page_kwarg = self.page_kwarg
        return self.paginate_queryset_by_page_kwarg(queryset, page_size, page_kwarg)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()

        queryset = object_list if object_list is not None else self.object_list
        page_size = self.get_paginate_by(queryset)

        user_worlds = self.get_user_worlds()
        context['user_worlds'] = user_worlds

        community_worlds = self.get_community_worlds()
        context_object_name = self.get_context_object_name(community_worlds)
        context[context_object_name] = community_worlds
        context['object_list'] = community_worlds

        if not page_size:  # pragma: no cover
            return context

        # User worlds
        paginator, page, queryset, is_paginated = self.paginate_user_worlds(page_size)
        context.update({
            'user_worlds_paginator': paginator,
            'user_worlds_page_obj': page,
            'user_worlds_is_paginated': is_paginated,
            'user_worlds': queryset,
            'user_worlds_full': user_worlds
        })

        # Community worlds
        paginator, page, queryset, is_paginated = self.paginate_community_worlds(page_size)
        context.update({
            'paginator': paginator,
            'page_obj': page,
            'is_paginated': is_paginated,
            'object_list': queryset,
            context_object_name: queryset,
            'object_list_full': community_worlds,
            context_object_name + '_full': community_worlds
        })

        return context


class WorldCreateView(LoginRequiredMixin, CreateView):
    form_class = forms.WorldForm
    model = models.Place
    success_url = reverse_lazy('roleplay:world_list')
    template_name = 'roleplay/world_create.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'user' in self.request.GET:
            kwargs.update({
                'user': self.request.user
            })
        return kwargs
