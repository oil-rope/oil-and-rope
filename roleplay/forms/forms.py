import logging
from typing import Optional, cast

from crispy_forms.helper import FormHelper
from django import forms
from django.apps import apps
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from mptt.forms import TreeNodeChoiceField

from common.constants import models as constants
from common.files import utils
from common.forms.mixins import FormCapitalizeMixin
from common.forms.widgets import DateTimeWidget, DateWidget, NameDisplayModelChoiceField
from registration.models import User

from .. import enums, models
from .layout import (CampaignFormLayout, PlaceLayout, RaceCampaignFormLayout, RaceFormLayout, RacePlaceFormLayout,
                     SessionFormLayout, WorldFormLayout)

LOGGER = logging.getLogger(__name__)

Chat = apps.get_model(constants.CHAT)


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
        exclude = ('owner', )
        model = models.Place

    def save(self, commit=True):
        parent_site = self.instance.parent_site
        self.instance.owner = parent_site.owner
        return super().save(commit)


class WorldForm(forms.ModelForm):
    def __init__(self, owner: User, public: bool = True, submit_text: str = _('create'), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.owner = owner
        self.public = public

        # NOTE: Using Meta options `help_texts` does not translate the help text.
        self.fields['image'].help_text = _('A picture is worth a thousand words. Max size file %(max_size)s MiB.') % {
            'max_size': utils.max_size_file_mb()
        }

        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.include_media = True
        self.helper.layout = WorldFormLayout(submit_text=submit_text)

    class Meta:
        exclude = ('user', 'parent_site', 'site_type', 'owner')
        model = models.Place

    def save(self, commit=True):
        self.instance: models.Place
        self.instance.owner = self.owner
        self.instance.site_type = enums.SiteTypes.WORLD
        self.instance.is_public = self.public
        return super().save(commit)


class CampaignForm(FormCapitalizeMixin, forms.ModelForm):
    """
    This form is used to create or update a campaign, this form also comes with a `TextField` to add players to
    the campaign.
    """

    email_invitations = forms.CharField(
        label=_('email invitations'),
        widget=forms.Textarea(attrs={'rows': 3, 'cols': 40}),
        required=False,
    )

    def __init__(self, user, submit_text=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if not submit_text:
            submit_text = _('create').capitalize()

        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.include_media = True
        self.helper.layout = CampaignFormLayout(submit_text)

    class Meta:
        fields = (
            'name', 'description', 'gm_info', 'summary', 'system', 'cover_image', 'is_public',
            'place', 'start_date', 'end_date',
        )
        model = models.Campaign
        widgets = {
            'start_date': DateWidget,
            'end_date': DateWidget,
        }

    def clean_email_invitations(self):
        email_invitations = self.cleaned_data.get('email_invitations')
        if email_invitations:
            return email_invitations.splitlines()
        return email_invitations

    def save(self, commit=True):
        if not self.instance.owner_id:
            # NOTE: This is a new campaign, so we need to set the owner.
            self.instance.owner = self.user
        self.instance = super().save(commit)
        return self.instance


class SessionForm(FormCapitalizeMixin, forms.ModelForm):
    def __init__(self, campaign, submit_text=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.campaign = campaign
        if not submit_text:
            submit_text = _('create').capitalize()

        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.layout = SessionFormLayout(submit_text)

    class Meta:
        model = models.Session
        fields = (
            'name', 'description', 'plot', 'gm_info', 'next_game', 'image',
        )
        widgets = {
            'next_game': DateTimeWidget,
        }

    def clean_next_game(self):
        next_game = self.cleaned_data.get('next_game')
        if next_game:
            if next_game < timezone.now():
                raise forms.ValidationError(_('next game date must be in the future.').capitalize())
        return next_game

    def save(self, commit=True):
        self.instance.campaign = self.campaign
        return super().save(commit)


class RacePlaceForm(FormCapitalizeMixin, forms.ModelForm):
    place = TreeNodeChoiceField(queryset=models.Place.objects.none())

    instance: models.Race
    user: User

    def __init__(self, user: User, place: Optional[models.Place], *args, **kwargs):
        super().__init__(*args, **kwargs)

        # User can only select place where they are owner
        place_field = cast(TreeNodeChoiceField, self.fields['place'])
        place_field.queryset = user.place_set.all()
        place_field.label = _('place').capitalize()
        # If initial place if given let's set it
        if place:
            place_field.initial = place
        self.fields['place'] = place_field

        self.instance.owner = user

        self.helper = FormHelper(self)
        self.helper.form_action = 'POST'
        self.helper.layout = RacePlaceFormLayout()

    class Meta:
        fields = (
            'place', 'name', 'description', 'strength', 'dexterity', 'constitution', 'intelligence', 'wisdom',
            'charisma', 'affected_by_armor',
        )
        model = models.Race


class RaceCampaignForm(FormCapitalizeMixin, forms.ModelForm):
    campaign = NameDisplayModelChoiceField(queryset=models.Campaign.objects.none())

    instance: models.Race
    user: User

    def __init__(self, user: User, campaign: Optional[models.Campaign], *args, **kwargs):
        super().__init__(*args, **kwargs)

        # User can only select place where they are owner
        campaign_field = cast(NameDisplayModelChoiceField, self.fields['campaign'])
        campaign_field.queryset = user.editable_campaigns()
        campaign_field.label = _('campaign').capitalize()
        # If initial place if given let's set it
        if campaign:
            campaign_field.initial = campaign
        self.fields['campaign'] = campaign_field

        self.instance.owner = user

        self.helper = FormHelper(self)
        self.helper.form_action = 'POST'
        self.helper.layout = RaceCampaignFormLayout()

    class Meta:
        fields = (
            'campaign', 'name', 'description', 'strength', 'dexterity', 'constitution', 'intelligence', 'wisdom',
            'charisma', 'affected_by_armor',
        )
        model = models.Race


class RaceForm(forms.ModelForm):

    def __init__(self, user=None, submit_text=_('create'), *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.user = user
        # self.owner = owner

        self.helper = FormHelper(self)
        self.helper.layout = RaceFormLayout(submit_text=submit_text)

    class Meta:
        fields = (
            'name',
            'description',
            'strength',
            'dexterity',
            'constitution',
            'intelligence',
            'wisdom',
            'charisma',
            'affected_by_armor',
        )

        model = models.Race
        help_texts = {
            'image': _(
                'A picture is worth a thousand words. Max size file %(max_size)s MiB.'
            ) % {'max_size': utils.max_size_file_mb()}
        }
