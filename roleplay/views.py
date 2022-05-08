import logging

from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.signing import BadSignature, TimestampSigner
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import resolve_url
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, ListView, RedirectView, UpdateView
from django.views.generic.detail import SingleObjectMixin

from common.constants import models
from common.mixins import OwnerRequiredMixin
from common.templatetags.string_utils import capfirstletter as cfl
from common.views import MultiplePaginatorListView
from roleplay.forms.layout import SessionFormLayout

from . import enums, forms
from .utils.invitations import send_session_invitations

LOGGER = logging.getLogger(__name__)

Campaign = apps.get_model(models.ROLEPLAY_CAMPAIGN)
Place = apps.get_model(models.ROLEPLAY_PLACE)
Session = apps.get_model(models.ROLEPLAY_SESSION)
User = get_user_model()


class PlaceCreateView(LoginRequiredMixin, OwnerRequiredMixin, CreateView):
    form_class = forms.PlaceForm
    model = Place
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
    model = Place
    template_name = 'roleplay/place/place_update.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'parent_site_queryset': self.object.get_root().get_family(),
            'submit_text': _('update'),
        })
        return kwargs


class PlaceDetailView(LoginRequiredMixin, DetailView):
    model = Place
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
    model = Place
    paginate_by = 3
    user_worlds_page_kwarg = 'page_user_worlds'
    queryset = Place.objects.filter(site_type=enums.SiteTypes.WORLD)
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
    model = Place
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

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper.form_action = resolve_url('roleplay:world:create')
        # NOTE: Since user is gotten from '?user' QueryParam, `form_action` must replicate this behavior
        if form.user:
            form.helper.form_action = f'{form.helper.form_action}?user'
        return form


class WorldUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    form_class = forms.WorldForm
    model = Place
    template_name = 'roleplay/place/place_update.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'owner': self.object.owner,
            'submit_text': _('update').capitalize()
        })

        return kwargs


class PlaceDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Place
    success_url = reverse_lazy('roleplay:world:list')
    template_name = 'roleplay/place/place_confirm_delete.html'


class CampaignPrivateListView(LoginRequiredMixin, ListView):
    """
    This view list :class:`~roleplay.models.Campaign` objects that the user is in players.
    """

    model = Campaign
    template_name = 'roleplay/campaign/campaign_private_list.html'

    def get_queryset(self):
        return super().get_queryset().filter(users__in=[self.request.user])


class CampaignDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Campaign
    template_name = 'roleplay/campaign/campaign_detail.html'

    def test_func(self):
        """
        Checks if user is in players otherwise they have no access.
        """

        campaign = self.get_object()
        if not campaign.is_public:
            return self.request.user in campaign.users.all()
        return True


class SessionCreateView(LoginRequiredMixin, CreateView):
    form_class = forms.SessionForm
    model = Session
    template_name = 'roleplay/session/session_create.html'

    def get_world(self):
        """
        Checks that given world exists and is not private.
        """

        world = self.get_available_worlds().filter(pk=self.kwargs['pk'])
        if world:
            return world.get()
        raise Http404()

    def get_initial(self):
        initial = super().get_initial()
        next_week = timezone.now() + timezone.timedelta(days=7)
        initial.update({
            'world': self.get_world(),
            'next_game': next_week.strftime('%Y-%m-%dT%H:%M'),
        })
        return initial

    def get_available_worlds(self):
        """
        Gets community maps and user's private maps.
        """

        qs = Place.objects.community_places()
        qs |= Place.objects.user_places(user=self.request.user)
        return qs.filter(site_type=enums.SiteTypes.WORLD).order_by('name')

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.add_game_masters(self.request.user)
        emails = form.cleaned_data.get('email_invitations', '').splitlines()
        send_session_invitations(self.object, self.request, emails)
        return response

    def get_success_url(self):
        return resolve_url(self.object)


class SessionJoinView(SingleObjectMixin, RedirectView):
    signer_class = TimestampSigner
    model = Session

    def get_signer_instace(self):
        return self.signer_class()

    def get_email_associated(self):
        try:
            signer = self.get_signer_instace()
            return signer.unsign(self.kwargs['token'], max_age=settings.PASSWORD_RESET_TIMEOUT)
        except BadSignature:
            raise Http404()

    def get_user(self):
        try:
            # If user is already logged in, use it
            if self.request.user.is_authenticated:
                return self.request.user
            return User.objects.get(email=self.get_email_associated())
        except User.DoesNotExist:
            return None

    def get_redirect_url(self, *args, **kwargs):
        session = self.get_object()
        user = self.get_user()
        if not user:
            messages.warning(self.request, _('you need an account to join this session.').capitalize())
            return resolve_url(settings.LOGIN_URL)
        session.players.add(self.get_user())
        messages.success(self.request, _('you have joined the session.').capitalize())
        return resolve_url(session)


class SessionDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Session
    template_name = 'roleplay/session/session_detail.html'

    def test_func(self):
        """
        Checks that user is in players.
        """

        session = self.get_object()
        return self.request.user in session.players.all()


class SessionDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Session
    success_url = reverse_lazy('roleplay:session:list')
    template_name = 'roleplay/session/session_confirm_delete.html'

    def test_func(self):
        """
        Checks that user is game master.
        """

        session = self.get_object()
        return self.request.user in session.game_masters

    def get_success_url(self):
        msg = _('session deleted.').capitalize()
        messages.success(self.request, msg)
        return super().get_success_url()


class SessionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    form_class = forms.SessionForm
    model = Session
    template_name = 'roleplay/session/session_update.html'

    def test_func(self):
        """
        Checks that user is game master.
        """

        session = self.get_object()
        return self.request.user in session.game_masters

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper.layout = SessionFormLayout(_('update').capitalize())
        return form

    def form_valid(self, form):
        response = super().form_valid(form)
        emails = form.cleaned_data.get('email_invitations', '').splitlines()
        send_session_invitations(self.object, self.request, emails)
        return response

    def get_success_url(self):
        msg = cfl(_('session updated!'))
        messages.success(self.request, msg)
        return reverse_lazy('roleplay:session:detail', kwargs={'pk': self.object.pk})


class SessionListView(LoginRequiredMixin, ListView):
    model = Session
    template_name = 'roleplay/session/session_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(campaign__users__in=[self.request.user])
