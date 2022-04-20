import logging

from crispy_forms.helper import FormHelper
from django import forms
from django.apps import apps
from django.db.models import QuerySet
from django.shortcuts import resolve_url
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from common.constants import models as constants
from common.files import utils
from common.forms.widgets import DateTimeWidget

from .. import enums, models
from .layout import PlaceLayout, RaceFormLayout, SessionFormLayout, WorldFormLayout

LOGGER = logging.getLogger(__name__)

Chat = apps.get_model(constants.CHAT_MODEL)


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
    next_game = forms.DateTimeField(
        widget=DateTimeWidget,
    )
    email_invitations = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={'rows': 3, 'cols': 40}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['email_invitations'].label = _('email invitations').capitalize()

        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.layout = SessionFormLayout()

    class Meta:
        model = models.Session
        fields = (
            'name', 'plot', 'next_game', 'system', 'world',
        )

    def clean_next_game(self):
        next_game = self.cleaned_data.get('next_game')
        if next_game:
            if next_game < timezone.now():
                raise forms.ValidationError(_('next game date must be in the future.').capitalize())
        return next_game

    def save(self, commit=True):
        self.instance = super().save(False)
        if commit:
            chat = Chat.objects.create(
                name=f'{self.instance.name} chat',
            )
            self.instance.chat = chat
        return super().save(commit)


class RaceForm(forms.ModelForm):

    def __init__(self, user=None, submit_text=_('create'), *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.user = user
        # self.owner = owner

        self.helper = FormHelper(self)
        self.helper.form_action = 'roleplay:race:create'
        self.helper.form_method = 'POST'
        self.helper.include_media = True
        self.helper.layout = RaceFormLayout(submit_text=submit_text)

    class Meta:
        exclude = ()
        model = models.Race
        help_texts = {
            'image': _(
                'A picture is worth a thousand words. Max size file %(max_size)s MiB.'
            ) % {'max_size': utils.max_size_file_mb()}
        }
