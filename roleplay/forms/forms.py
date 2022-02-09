import asyncio
import logging
import pathlib
from smtplib import SMTPAuthenticationError

from crispy_forms.helper import FormHelper
from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from common.files import utils
from common.forms.widgets import DateWidget, TimeWidget

from .. import enums, models
from .layout import SessionFormLayout, WorldFormLayout

LOGGER = logging.getLogger(__name__)


class PlaceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.include_media = True

    class Meta:
        exclude = ('user', 'owner')
        help_texts = {
            'image': _(
                'A picture is worth a thousand words. Max size file %(max_size)s MiB.'
            ) % {'max_size': utils.max_size_file_mb()}
        }
        model = models.Place


class WorldForm(forms.ModelForm):

    def __init__(self, owner, user=None, submit_text=_('create'), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.owner = owner

        self.helper = FormHelper(self)
        self.helper.form_action = 'roleplay:world:create'
        self.helper.form_method = 'POST'
        self.helper.include_media = True
        self.helper.layout = WorldFormLayout(submit_text=submit_text)

    class Meta:
        exclude = ('user', 'parent_site', 'site_type', 'owner')
        model = models.Place
        help_texts = {
            'image': _(
                'A picture is worth a thousand words. Max size file %(max_size)s MiB.'
            ) % {'max_size': utils.max_size_file_mb()}
        }

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
        css_file = pathlib.Path(f'{settings.BASE_DIR}/core/static/core/css/oilandrope-theme.min.css')
        html_msg = render_to_string(
            'email_templates/invitation_email.html',
            context={
                'style': css_file.read_text(encoding='utf-8'),
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
