from typing import TYPE_CHECKING, cast

from dateutil.relativedelta import relativedelta
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import resolve_url
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from bot.models import User as DiscordUser
from common.constants import models as constants
from common.files.upload import default_upload_to
from core.models import TracingMixin

if TYPE_CHECKING:
    from roleplay.models import Campaign as CampaignModel
    from roleplay.models import Place as PlaceModel
    from roleplay.models import Session as SessionModel


class User(AbstractUser):
    email = models.EmailField(verbose_name=_('email address'), null=False, blank=False, unique=True)
    is_premium = models.BooleanField(verbose_name=_('premium user'), default=False)
    discord_id = models.CharField(
        verbose_name=_('discord identifier'), max_length=100, null=False, blank=True,
    )

    @classmethod
    def get_bot(cls):
        return cls.objects.get(username='Oil & Rope Bot')

    @property
    def discord_user(self):
        if not self.discord_id:
            return None
        return DiscordUser(self.discord_id)

    @property
    def sessions(self):
        Session: 'SessionModel' = apps.get_model(constants.ROLEPLAY_SESSION)
        sessions = Session.objects.filter(campaign__users__in=[self])
        return sessions

    def accessible_places(self):
        Place: 'PlaceModel' = apps.get_model(constants.ROLEPLAY_PLACE)
        community_places = Place.objects.community_places()
        private_places = Place.objects.filter(is_public=False, owner=self)
        return cast(models.QuerySet['PlaceModel'], community_places ^ private_places)

    def editable_campaigns(self):
        """
        This method will return all campaigns where user is able to edit (either by being owner or GameMaster).
        """

        owned_campaigns = self.campaign_owned_set.all()
        is_game_master_campaigns = self.campaign_set.filter(player_in_campaign_set__is_game_master=True)
        return cast(models.QuerySet['CampaignModel'], owned_campaigns ^ is_game_master_campaigns)

    @cached_property
    def has_editable_campaigns(self):
        """
        Performance-wise property for checking (and caching) whether a user has editable campaigns (as Game Master or
        Owner).

        Returns
        -------
        has_editable_campaigns: :class:`bool`
            True if user can edit any campaign. False otherwise.
        """

        return self.editable_campaigns().exists()

    def get_absolute_url(self):
        return resolve_url('registration:user:edit', pk=self.pk)

    class Meta:
        db_table = 'auth_user'
        verbose_name = _('user')
        verbose_name_plural = _('users')


class Profile(TracingMixin):
    """
    This model manages User's profile.

    Parameters
    -----------
    user: :class:`User`
        The user.
    bio: Optional[:class:`str`]
        Biography of the user.
    birthday: Optional[:class:`datetime.date`]
        User's birthday.
    language: :class:`str`
        User's language.
    alias: Optional[:class:`str`]
        Alias for the user if wanted.
    web: Optional[:class:`str`]
        User's personal website.
    image: Optional[:class:`Storage`]
        User's avatar.

    Attributes
    -----------
    age: :class:`int`
        User's age.
    """

    user = models.OneToOneField(
        to=constants.REGISTRATION_USER, on_delete=models.CASCADE, related_name='profile', verbose_name=_('user'),
    )
    bio = models.TextField(verbose_name=_('biography'), null=False, blank=True)
    birthday = models.DateField(verbose_name=_('birthday'), null=True, blank=True)

    language = models.CharField(
        verbose_name=_('language'), choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE, max_length=10,
    )
    web = models.URLField(verbose_name=_('website'), max_length=200, blank=True, null=False)
    image = models.ImageField(
        verbose_name=_('avatar'), upload_to=default_upload_to, blank=True, null=False,
    )

    @property
    def age(self):
        r_delta = relativedelta(timezone.datetime.today().date(), self.birthday)
        return r_delta.years

    # Metadata
    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')
        ordering = ['user__username', 'user__first_name']

    def __str__(self):
        return 'Profile {}'.format(self.user.username)


@receiver(post_save, sender=get_user_model())
def create_profile_post_save_receiver(instance, **kwargs):
    """
    Creates a :class:`Profile` once a :class:`registration.User` is created.
    """

    if kwargs.get('created', False):
        Profile.objects.create(user=instance)
