import asyncio
import logging
import pathlib
from smtplib import SMTPAuthenticationError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Column, Field, Fieldset, Layout, Reset, Row, Submit
from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from common.files import utils
from common.forms.widgets import DateWidget, TimeWidget
from . import enums, models

LOGGER = logging.getLogger(__name__)


class WorldForm(forms.ModelForm):

    def __init__(self, owner, user=None, submit_text=_('Create'), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.owner = owner
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(
                Column(
                    Field('name', placeholder='Middle-Earth, Narnia, Argos...'),
                    css_class='col-12 col-lg-7'
                ),
                Column(
                    Field('description',
                          placeholder=_('Write something about your world, its civilizations, its culture...')),
                    css_class='col-12 col-lg-7'
                ),
                Column(
                    Field('image'),
                    css_class='col-12 col-lg-7'
                ),
                css_class='justify-content-lg-around'
            ),
            Row(
                Submit('submit', submit_text, css_class='btn btn-primary col-5 col-lg-6'),
                Reset('reset', _('Clean'), css_class='btn btn-secondary col-5 d-lg-none'),
                css_class='justify-content-around'
            )
        )

    class Meta:
        exclude = ('user', 'parent_site', 'site_type', 'owner')
        model = models.Place
        help_texts = {
            'image': '{}. {} {} MiB.'.format(
                _('A picture is worth a thousand words'), _('Max size file'), utils.max_size_file_mb()
            )
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
        initial=timezone.now().date(),
        required=True,
    )
    next_game_time = forms.TimeField(
        label='',
        widget=TimeWidget,
        initial=timezone.now().time().strftime('%H:%M'),
        required=True,
    )
    invited_players = forms.MultipleChoiceField(
        label='',
        choices=(),
        required=False,
        help_text=_('Listed players will be notified'),
    )
    invite_player_input = forms.EmailField(
        label='',
        required=False,
        help_text=_('Type and email'),
    )

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.game_master = request.user

        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(
                Column('name'),
                Column('system'),
                Column('world'),
            ),
            Row(
                Column('description'),
            ),
            Fieldset(
                _('Next session'),
                Column('next_game_date', css_class='col-6'),
                Column('next_game_time', css_class='col-6'),
                css_class='form-row text-center',
            ),
            Fieldset(
                _('Invite players'),
                Column(Field('invited_players', id='playersInvitedContainer')),
                Column(Field('invite_player_input', id='invitePlayerInput')),
                Column(
                    Button('', _('Add'), css_class='btn btn-info w-100', css_id='playerAddButton'),
                    css_class='form-group',
                ),
                css_class='form-row text-center',
            ),
            Row(
                Column(
                    Submit('submit', _('Create'), css_class='w-100'),
                    css_class='col-md-6'
                ),
                css_class='justify-content-md-center',
            ),
        )

    class Meta:
        model = models.Session
        exclude = ('chat', 'game_master', 'next_game', 'players',)

    async def send_invitations(self):
        css_file = pathlib.Path(f'{settings.STATIC_ROOT}core/css/oilandrope-theme.min.css')
        html_msg = render_to_string(
            'email_templates/invitation_email.html',
            context={
                'style': css_file.read_text(encoding='utf-8'),
                'protocol': 'https' if self.request.is_secure() else 'http',
                'domain': self.request.META.get('HTTP_HOST', 'localhost'),
                'object': self.instance,
            }
        )
        subject = _('You\'ve been invited to %(world)s!') % {'world': self.instance.name}
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

    # noinspection PyAttributeOutsideInit
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
