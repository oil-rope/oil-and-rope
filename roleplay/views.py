import logging
from typing import TYPE_CHECKING

from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.core.signing import BadSignature, TimestampSigner
from django.db.models import OuterRef, Prefetch, Subquery
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, resolve_url
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, ListView, RedirectView, UpdateView
from django.views.generic.detail import SingleObjectMixin
from django_filters.views import FilterView

from common.constants import models
from common.mixins import OwnerRequiredMixin
from common.templatetags.string_utils import capfirstletter as cfl
from common.tools import HtmlThreadMail
from common.views import MultiplePaginatorListView
from roleplay.managers import PlaceQuerySet

from . import enums, filters, forms
from .forms.layout import SessionFormLayout
from .mixins import UserInAllWithRelatedNameMixin
from .utils.invitations import send_campaign_invitations

if TYPE_CHECKING:
    from django.contrib.contenttypes.models import ContentType as ContentTypeModel

    from common.models import Vote as VoteModel
    from registration.models import User as UserModel
    from roleplay.models import Campaign as CampaignModel
    from roleplay.models import Place as PlaceModel
    from roleplay.models import PlayerInCampaign as PlayerInCampaignModel
    from roleplay.models import Race as RaceModel
    from roleplay.models import Session as SessionModel

LOGGER = logging.getLogger(__name__)

Campaign: 'CampaignModel' = apps.get_model(models.ROLEPLAY_CAMPAIGN)
ContentType: 'ContentTypeModel' = apps.get_model(models.CONTENT_TYPE)
Place: 'PlaceModel' = apps.get_model(models.ROLEPLAY_PLACE)
PlayerInCampaign: 'PlayerInCampaignModel' = apps.get_model(models.ROLEPLAY_PLAYER_IN_CAMPAIGN)
Race: 'RaceModel' = apps.get_model
Session: 'SessionModel' = apps.get_model(models.ROLEPLAY_SESSION)
User: 'UserModel' = get_user_model()
Vote: 'VoteModel' = apps.get_model(models.COMMON_VOTE)


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

        # Community world
        if self.object.is_public:
            return response

        # Private world
        if not self.object.is_public and self.object.owner == request.user:
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

    def get_queryset(self) -> PlaceQuerySet:
        return super().get_queryset().filter(site_type=enums.SiteTypes.WORLD)

    def get_private_worlds(self):
        user = self.request.user
        qs = self.get_queryset()
        return qs.filter(owner=user, is_public=False)

    def get_community_worlds(self):
        qs = self.get_queryset()
        return qs.community_places()

    def paginate_user_worlds(self, page_size):
        queryset = self.get_private_worlds()
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

        user_worlds = self.get_private_worlds()
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
                'public': False
            })
        return kwargs

    def get_form(self, form_class=None):
        form: forms.WorldForm = super().get_form(form_class)
        form.helper.form_action = resolve_url('roleplay:world:create')
        # NOTE: Since user is gotten from '?user' QueryParam, `form_action` must replicate this behavior
        if form.public:
            form.helper.form_action = f'{form.helper.form_action}?user'
        return form


class WorldUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    form_class = forms.WorldForm
    model = Place
    template_name = 'roleplay/place/place_update.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.object: 'PlaceModel'
        kwargs.update({
            'owner': self.object.owner,
            'submit_text': _('update').capitalize()
        })

        return kwargs


class PlaceDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Place
    success_url = reverse_lazy('roleplay:world:list')
    template_name = 'roleplay/place/place_confirm_delete.html'


class CampaignCreateView(LoginRequiredMixin, CreateView):
    form_class = forms.CampaignForm
    model = Campaign
    template_name = 'roleplay/campaign/campaign_create.html'

    def get_world(self):
        world_pk = self.kwargs.get('world_pk')
        return get_object_or_404(Place, pk=world_pk)

    def get_initial(self):
        initial = super().get_initial()
        initial.update({
            'place': self.get_world(),
        })
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
            'submit_text': _('create').capitalize(),
        })
        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper.form_action = resolve_url('roleplay:campaign:create', world_pk=self.kwargs['world_pk'])
        form.fields['place'].queryset = self.request.user.accessible_places().filter(
            site_type=enums.SiteTypes.WORLD,
        )
        return form

    def form_valid(self, form):
        response = super().form_valid(form)
        emails = form.cleaned_data['email_invitations']
        send_campaign_invitations(self.object, self.request, emails)
        self.object.add_game_masters(self.request.user)
        return response

    def get_success_url(self):
        return self.object.get_absolute_url()


class CampaignJoinView(SingleObjectMixin, RedirectView):
    signer_class = TimestampSigner
    model = Campaign

    def get_signer_instance(self):
        return self.signer_class()

    def get_email_associated(self):
        try:
            signer = self.get_signer_instance()
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
        instance = self.get_object()
        user = self.get_user()
        if not user:
            messages.warning(self.request, _('you need an account to join this campaign.').capitalize())
            return resolve_url(settings.LOGIN_URL)
        instance.users.add(self.get_user())
        messages.success(self.request, _('you have joined the campaign.').capitalize())
        return resolve_url(instance)


class CampaignComplexQuerySetMixin:
    model = Campaign
    # NOTE: Since this declaration is complex enough we'll write it down in `get_queryset`
    queryset = None

    def get_queryset(self):
        self.queryset = Campaign.objects.with_votes().select_related('owner')

        # Adding last session so we avoid SQL queries
        sessions_finished = Session.objects.finished().filter(
            campaign=OuterRef('pk'),
        ).order_by('-next_game')
        self.queryset = self.queryset.annotate(
            last_session_date=Subquery(sessions_finished.values('next_game')[:1])
        )

        # Adding if the user is GM so we avoid SQL queries
        self.queryset = self.queryset.annotate(
            user_is_game_master=Subquery(
                PlayerInCampaign.objects.filter(
                    campaign=OuterRef('pk'),
                    user=self.request.user,
                ).values('is_game_master')
            )
        )

        # NOTE: This will return `True` or `False` and `None` if user hasn't voted yet
        self.queryset = self.queryset.annotate(
            user_vote=Subquery(
                Vote.objects.filter(
                    content_type=ContentType.objects.get_for_model(Campaign),
                    object_id=OuterRef('pk'),
                    user=self.request.user,
                ).values('is_positive')[:1]
            ),
        )

        return super().get_queryset()


class CampaignListView(LoginRequiredMixin, CampaignComplexQuerySetMixin, FilterView):
    """
    This view handles the list of campaigns that are public.
    """

    filterset_class = filters.CampaignFilter
    model = Campaign
    ordering = ('-total_votes', 'name', '-entry_created_at')
    paginate_by = 6
    template_name = 'roleplay/campaign/campaign_list.html'

    def get_queryset(self):
        return super().get_queryset().filter(is_public=True)


class CampaignUserListView(LoginRequiredMixin, CampaignComplexQuerySetMixin, ListView):
    """
    This view list :class:`~roleplay.models.Campaign` objects that the user is in players.
    """

    model = Campaign
    ordering = ('-total_votes', 'name', '-entry_created_at')
    paginate_by = 6
    template_name = 'roleplay/campaign/campaign_private_list.html'

    def get_queryset(self):
        return super().get_queryset().filter(
            users=self.request.user
        )


class CampaignDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Campaign
    # NOTE: Since this declaration is complex enough we'll write it down in `get_queryset`
    queryset = None
    template_name = 'roleplay/campaign/campaign_detail.html'

    def post(self, *args, **kwargs):
        # If a post request is made, we'll send a message to GMs in order for the user to join campaign
        HtmlThreadMail(
            'email_templates/campaign_join_request.html',
            request=self.request,
            context={'user': self.request.user, 'object': self.object},
            subject=cfl(_('new player wants to join your adventure!')),
            to=[gm.email for gm in self.object.game_masters],
        ).send()
        messages.success(
            self.request,
            _('You\'ve requested to join this adventure. Once the GMs accepts your request, you\'ll receive an email.'),
        )
        return redirect(self.object)

    def get_queryset(self):
        # NOTE: The complexity of this queryset will allow us to not repeat the same SQL query
        self.queryset = Campaign.objects.prefetch_related(
            Prefetch('users', queryset=User.objects.select_related('profile')),
            'session_set',
        ).select_related('owner').with_votes()
        return super().get_queryset()

    def get_object(self, queryset=None):
        """
        We override this method to ensure `self.object` is not retrieved again.
        """

        if hasattr(self, 'object'):
            return self.object
        return super().get_object(queryset)

    def test_func(self):
        """
        Checks if user is in players otherwise they have no access.
        """

        self.object = self.get_object()
        if self.object.is_public:
            return True
        # NOTE: We don't use `values_list` with `flat=True` since we do a `prefetch_related`
        if self.request.user in self.object.users.all():
            return True
        if self.request.user == self.object.owner:
            return True
        return False


class CampaignUpdateView(LoginRequiredMixin, UserInAllWithRelatedNameMixin, UpdateView):
    form_class = forms.CampaignForm
    model = Campaign
    related_name_attr = 'game_masters'
    template_name = 'roleplay/campaign/campaign_update.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
            'submit_text': _('update').capitalize()
        })
        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper.form_action = resolve_url('roleplay:campaign:edit', pk=self.object.pk)
        form.fields['place'].queryset = self.request.user.accessible_places().filter(
            site_type=enums.SiteTypes.WORLD,
        )
        return form

    def form_valid(self, form):
        response = super().form_valid(form)
        emails = form.cleaned_data['email_invitations']
        send_campaign_invitations(self.object, self.request, emails)
        return response

    def get_success_url(self):
        return resolve_url(self.object)


class CampaignDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Campaign
    success_url = reverse_lazy('roleplay:campaign:list-private')
    template_name = 'roleplay/campaign/campaign_confirm_delete.html'

    def get_success_url(self):
        msg = _('campaign deleted successfully.').capitalize()
        messages.success(self.request, msg)
        return super().get_success_url()


class SessionCreateView(LoginRequiredMixin, CreateView):
    form_class = forms.SessionForm
    model = Session
    template_name = 'roleplay/session/session_create.html'

    def get_campaign(self):
        # Only Game Masters can create sessions for a campaign
        campaign_qs = Campaign.objects.annotate(
            user_is_game_master=Subquery(
                PlayerInCampaign.objects.filter(
                    campaign=OuterRef('pk'),
                    user=self.request.user,
                ).values('is_game_master')
            )
        ).filter(user_is_game_master=True)
        return get_object_or_404(campaign_qs, pk=self.kwargs['campaign_pk'])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'campaign': self.get_campaign(),
        })
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        next_week = timezone.now() + timezone.timedelta(days=7)
        initial.update({
            'next_game': next_week.strftime('%Y-%m-%dT%H:%M'),
        })
        return initial

    def get_success_url(self):
        return resolve_url(self.object)


class SessionDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Session
    queryset = Session.objects.select_related(
        'campaign'
    ).prefetch_related(
        Prefetch('campaign__users', queryset=User.objects.select_related('profile')),
    )
    template_name = 'roleplay/session/session_detail.html'

    def get_queryset(self):
        qs = super().get_queryset().annotate(
            user_is_game_master=Subquery(
                PlayerInCampaign.objects.filter(
                    campaign=OuterRef('campaign'),
                    user=self.request.user,
                ).values('is_game_master')
            )
        )
        return qs

    def get_object(self, queryset=None):
        if hasattr(self, 'object'):
            return self.object
        return super().get_object(queryset)

    def test_func(self):
        """
        Checks that user is in players.
        """

        self.object = self.get_object()
        return self.request.user in self.object.campaign.users.all()


class SessionDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Session
    success_url = reverse_lazy('roleplay:session:list')
    template_name = 'roleplay/session/session_confirm_delete.html'

    def test_func(self):
        """
        Checks that user is game master.
        """

        self.object = self.get_object()
        return self.request.user in self.object.campaign.game_masters

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
        return self.request.user in session.campaign.game_masters

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'campaign': self.object.campaign,
        })
        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper.layout = SessionFormLayout(_('update').capitalize())
        return form

    def form_valid(self, form):
        response = super().form_valid(form)
        emails = form.cleaned_data.get('email_invitations', '').splitlines()
        send_campaign_invitations(self.object, self.request, emails)
        return response

    def get_success_url(self):
        msg = cfl(_('session updated!'))
        messages.success(self.request, msg)
        return reverse_lazy('roleplay:session:detail', kwargs={'pk': self.object.pk})


class SessionListView(LoginRequiredMixin, FilterView):
    filterset_class = filters.SessionFilter
    model = Session
    paginate_by = 6
    queryset = Session.objects.select_related(
        'campaign'
    ).prefetch_related(
        Prefetch('campaign__users', queryset=User.objects.select_related('profile')),
    )
    template_name = 'roleplay/session/session_list.html'

    def get_filterset(self, filterset_class):
        filterset = super().get_filterset(filterset_class)
        filterset.filters['campaign'].queryset = Campaign.objects.filter(
            users=self.request.user,
        )
        return filterset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['TABLETOP_URL'] = settings.TABLETOP_URL
        return context


class RaceCreateView(LoginRequiredMixin, CreateView):
    """
    This view creates a race
    """

    form_class = forms.RaceForm
    model = Race
    template_name = 'roleplay/race/race_create.html'

    def get_success_url(self):
        return resolve_url(self.object)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
            'submit_text': _('create').capitalize()
        })

        return kwargs


class RaceDetailView(LoginRequiredMixin, DetailView):
    """
    This view shows the details of a race
    """

    model = Race
    template_name = 'roleplay/race/race_detail.html'


class RaceUpdateView(LoginRequiredMixin, UpdateView, UserPassesTestMixin):
    """
    This view updates a race
    """

    model = Race
    form_class = forms.RaceForm
    template_name = 'roleplay/race/race_update.html'

    def get_form_kwargs(self, form_class=None):
        kwargs = super().get_form_kwargs()
        kwargs['submit_text'] = _('update').capitalize()

        user = self.request.user
        instance = self.get_object()

        if user not in instance.users.all():
            raise PermissionDenied

        return kwargs

    def get_success_url(self):
        return reverse_lazy('roleplay:race:detail', kwargs={'pk': self.object.pk})


class RaceListView(LoginRequiredMixin, ListView):
    """
    this view deletes a race
    """

    model = Race
    template_name = 'roleplay/race/race_list.html'
    paginate_by = 10
    queryset = Race.objects.all()


class RaceDeleteView(LoginRequiredMixin, DeleteView):
    """
    this view deletes a race
    """

    model = Race
    success_url = reverse_lazy('roleplay:race:list')
    template_name = 'roleplay/race/race_confirm_delete.html'

    def get_queryset(self):
        qs = super().get_queryset().filter(
            users=self.request.user,
        )
        return qs
