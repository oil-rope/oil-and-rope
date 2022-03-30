import asyncio
import logging
from smtplib import SMTPAuthenticationError

from crispy_forms.helper import FormHelper
from django import forms
from django.core.mail import send_mail
from django.db.models import QuerySet
from django.shortcuts import resolve_url
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from common.files import utils
from common.forms.widgets import DateWidget, TimeWidget

from .. import enums, models
from .layout import PlaceLayout, SessionFormLayout, WorldFormLayout

LOGGER = logging.getLogger(__name__)


class PlaceForm(forms.ModelForm):
    def __init__(self, parent_site_queryset=None, submit_text=_('create'), *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['parent_site'].label = _('this place belongs to...').capitalize()
        self.fields['parent_site'].required = True
        if parent_site_queryset and isinstance(parent_site_queryset, QuerySet):
            self.fields['parent_site'].queryset = parent_site_queryset

        # NOTE: Using Meta options `help_texts` does not translate the help text.
        self.fields['image'].help_text = _('A picture is worth a thousand words. Max size file %(max_size)s MiB.') % {
            'max_size': utils.max_size_file_mb()
        }

        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.include_media = True
        self.helper.layout = PlaceLayout(submit_text)

    class Meta:
        exclude = ('owner', 'user')
        model = models.Place

    def save(self, commit=True):
        parent_site = self.instance.parent_site
        self.instance.owner = parent_site.owner
        self.instance.user = parent_site.user
        return super().save(commit)


class WorldForm(forms.ModelForm):

    def __init__(self, owner, user=None, submit_text=_('create'), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.owner = owner

        # NOTE: Using Meta options `help_texts` does not translate the help text.
        self.fields['image'].help_text = _('A picture is worth a thousand words. Max size file %(max_size)s MiB.') % {
            'max_size': utils.max_size_file_mb()
        }

        self.helper = FormHelper(self)
        self.helper.form_action = resolve_url('roleplay:world:create')
        # NOTE: Since user is gotten from '?user? QueryParam, `form_action` must replicate this behavior
        if self.user:
            self.helper.form_action = f'{self.helper.form_action}?user'
        self.helper.form_method = 'POST'
        self.helper.include_media = True
        self.helper.layout = WorldFormLayout(submit_text=submit_text)

    class Meta:
        exclude = ('user', 'parent_site', 'site_type', 'owner')
        model = models.Place

    def save(self, commit=True):
        if self.user:
            self.instance.user = self.user
        self.instance.owner = self.owner
        self.instance.site_type = enums.SiteTypes.WORLD
        return super().save(commit)


class SessionForm(forms.ModelForm):
    next_game_date = forms.DateField(
        label='',
        widget=DateWidget,
        required=True,
    )
    next_game_time = forms.TimeField(
        label='',
        widget=TimeWidget,
        required=True,
    )
    invited_players = forms.MultipleChoiceField(
        label='',
        choices=(),
        required=False,
        help_text=_('listed players will be notified'),
    )
    invite_player_input = forms.EmailField(
        label='',
        required=False,
        help_text=_('type an email'),
    )

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)

        invited_players_field = self.fields['invited_players']
        invited_players_field.help_text = invited_players_field.help_text.capitalize()
        invite_player_input_field = self.fields['invite_player_input']
        invite_player_input_field.help_text = invite_player_input_field.help_text.capitalize()

        self.request = request
        self.game_master = request.user

        self.helper = FormHelper(self)
        self.helper.layout = SessionFormLayout()

    class Meta:
        model = models.Session
        exclude = ('chat', 'game_master', 'next_game', 'players',)

    async def send_invitations(self):
        html_msg = render_to_string(
            'email_templates/invitation_email.html',
            context={
                'protocol': 'https' if self.request.is_secure() else 'http',
                'domain': self.request.META.get('HTTP_HOST', 'localhost'),
                'object': self.instance,
            }
        )
        subject = _('you\'ve been invited to %(world)s!').capitalize() % {'world': self.instance.name}
        invitations = self.cleaned_data['invited_players']

        try:
            send_mail(
                subject=subject,
                message='',
                from_email=None,
                recipient_list=invitations,
                html_message=html_msg
            )
        except SMTPAuthenticationError:  # pragma: no cover
            LOGGER.exception('Unable to logging email server with given credentials.')

    def clean(self):
        cleaned_data = super().clean()

        next_game_date = cleaned_data.get('next_game_date')
        next_game_time = cleaned_data.get('next_game_time')
        if next_game_date and next_game_time:
            self.next_game = timezone.datetime.combine(
                date=next_game_date, time=next_game_time, tzinfo=timezone.get_current_timezone()
            )

    def save(self, commit=True):
        self.instance.game_master = self.game_master
        self.instance = super().save(commit)

        self.instance.next_game = self.next_game
        if commit:
            self.instance.save()

        asyncio.run(self.send_invitations())

        return self.instance
