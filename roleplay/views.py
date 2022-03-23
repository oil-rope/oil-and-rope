import json
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, RedirectView, UpdateView
from django.views.generic.detail import SingleObjectMixin
from rest_framework.authtoken.models import Token

from api.serializers.registration import UserSerializer
from common.mixins import OwnerRequiredMixin
from common.templatetags.string_utils import capfirstletter as cfl
from common.views import MultiplePaginatorListView

from common.forms.layout import SubmitClearLayout as Submit

from . import enums, forms, models

LOGGER = logging.getLogger(__name__)


class PlaceCreateView(LoginRequiredMixin, OwnerRequiredMixin, CreateView):
    form_class = forms.PlaceForm
    model = models.Place
    template_name = 'roleplay/place/place_create.html'

    def get_parent_site(self):
        parent_site = self.model.objects.get(pk=self.kwargs['pk'])
        return parent_site

    def get_site_type(self):
        site_type = int(self.request.GET.get('site_type', enums.SiteTypes.CITY))
        return site_type

    def get_initial(self):
        initial = super().get_initial()
        initial.update({
            'site_type': self.get_site_type(),
            'parent_site': self.get_parent_site(),
        })
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'parent_site_queryset': self.get_parent_site().get_descendants(include_self=True),
        })
        return kwargs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['parent_site'] = self.get_parent_site()
        return context


class PlaceUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    form_class = forms.PlaceForm
    model = models.Place
    template_name = 'roleplay/place/place_update.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'parent_site_queryset': self.object.get_root().get_family(),
            'submit_text': _('update'),
        })
        return kwargs


class PlaceDetailView(LoginRequiredMixin, DetailView):
    model = models.Place
    template_name = 'roleplay/place/place_detail.html'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        user = request.user

        # Community world
        if not self.object.user or not self.object.owner:
            return response

        # Private world
        if user == self.object.user:
            return response

        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['world_structure'] = self.object.get_descendants(include_self=True)

        return context


class WorldListView(LoginRequiredMixin, MultiplePaginatorListView):
    enum = enums.SiteTypes
    model = models.Place
    paginate_by = 3
    user_worlds_page_kwarg = 'page_user_worlds'
    queryset = models.Place.objects.filter(site_type=enums.SiteTypes.WORLD)
    template_name = 'roleplay/world/world_list.html'

    def get_user_worlds(self):
        user = self.request.user
        return self.model.objects.user_places(user=user.id).filter(site_type=self.enum.WORLD)

    def get_community_worlds(self):
        return self.model.objects.community_places().filter(site_type=self.enum.WORLD)

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
    template_name = 'roleplay/world/world_create.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        kwargs.update({
            'owner': user
        })
        if 'user' in self.request.GET:
            kwargs.update({
                'user': user
            })
        return kwargs


class WorldUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    form_class = forms.WorldForm
    model = models.Place
    template_name = 'roleplay/place/place_update.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'owner': self.object.owner,
            'submit_text': _('update').capitalize()
        })

        return kwargs


class WorldDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = models.Place
    success_url = reverse_lazy('roleplay:world:list')
    template_name = 'roleplay/world/world_confirm_delete.html'


class SessionCreateView(LoginRequiredMixin, CreateView):
    form_class = forms.SessionForm
    model = models.Session
    template_name = 'roleplay/session/session_create.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'request': self.request,
        })
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        initial.update({
            'next_game_date': timezone.now().strftime('%Y-%m-%d'),
            'next_game_time': timezone.now().strftime('%H:%M'),
        })
        return initial

    def get_worlds(self):
        """
        Gets either community maps or user's private maps.
        """

        qs = models.Place.objects.community_places()
        qs.union(models.Place.objects.user_places(self.request.user))
        return qs

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['world'].queryset = self.get_worlds()

        if self.request.method == 'POST':
            invited_users = self.request.POST.getlist('invited_players')
            if not invited_users:
                return form
            # Little hack to avoid empty choices validation
            form.fields['invited_players'].choices = ((email, email) for email in invited_users)

        return form


class SessionJoinView(LoginRequiredMixin, SingleObjectMixin, RedirectView):
    """
    Adds the player to the session.
    """

    model = models.Session
    pattern_name = 'roleplay:session:detail'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = request.user
        self.object.players.add(user)
        response = super().get(request, *args, **kwargs)
        return response


class SessionDetailView(LoginRequiredMixin, DetailView):
    """
    This view controls active session for user.
    """

    model = models.Session
    template_name = 'roleplay/session/session_detail.html'

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        self.object = self.get_object()
        players = self.object.players.all()

        if user not in players:
            msg = cfl(_('you are not part of this session!'))
            messages.error(request, msg)
            return HttpResponseForbidden(content=msg)

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.add_user_to_chat()
        return super().get(request, *args, **kwargs)

    def get_chat(self):
        return self.object.chat

    def add_user_to_chat(self):
        chat = self.get_chat()
        chat.users.add(self.request.user)

    def _check_user_has_token(self):
        Token.objects.get_or_create(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self._check_user_has_token()
        context['serialized_user'] = json.dumps(UserSerializer(self.request.user).data)
        return context


class RaceCreateView(CreateView):
    """
    This view creates a race
    """

    form_class = forms.RaceForm
    model = models.Race
    template_name = 'roleplay/race/race_create.html'

    def get_success_url(self):
        return reverse_lazy('roleplay:race:detail', kwargs={'pk': self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['submit_text']: _('create').capitalize()

        return kwargs


class RaceDetailView(LoginRequiredMixin, DetailView):
    """
    This view shows the details of a race
    """

    model = models.Race
    template_name = 'roleplay/race/race_detail.html'


class RaceUpdateView(LoginRequiredMixin, UpdateView):
    """
    This view updates a race
    """

    model = models.Race
    form_class = forms.RaceForm
    template_name = 'roleplay/race/race_update.html'

    def get_form_kwargs(self, form_class=None):
        breakpoint()
        kwargs['submit_text'] = _('update').capitalize()
        return kwargs

    def get_success_url(self):
        return reverse_lazy('roleplay:race:detail', kwargs={'pk': self.object.pk})

class RaceListView(LoginRequiredMixin, DeleteView):
    """
    this view deletes a race
    """

    model = models.Race
    success_url = reverse_lazy('roleplay:race:list')
    template_name = 'roleplay/race/race_list.html'
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()

        return context

class RaceDeleteView(LoginRequiredMixin, DeleteView):
    """
    this view deletes a race
    """

    model = models.Race
    success_url = reverse_lazy('roleplay:race:list')
    template_name = 'roleplay/race/race_confirm_delete.html'
