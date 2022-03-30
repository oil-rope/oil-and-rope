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
from django.utils.functional import cached_property, keep_lazy
from django.utils.translation import gettext_lazy as _

from bot.models import User as DiscordUser
from common.constants import models as constants
from common.files.upload import default_upload_to
from core.models import TracingMixin
from dynamic_menu.enums import MenuTypes


class User(AbstractUser):
    email = models.EmailField(verbose_name=_('email address'), null=False, blank=False, unique=True)
    is_premium = models.BooleanField(verbose_name=_('premium user'), default=False)
    discord_id = models.CharField(
        verbose_name=_('discord identifier'), max_length=100, null=False, blank=True,
    )

    @property
    def discord_user(self):
        if not self.discord_id:
            return None
        return DiscordUser(self.discord_id)

    @property
    def owned_races(self):
        races = self.race_set.filter(
            m2m_race_set__is_owner=True
        )
        return races

    @property
    @keep_lazy(models.QuerySet)
    def gm_sessions(self):
        sessions = self.session_set.filter(
            player_in_session_set__is_game_master=True
        )
        return sessions

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
        to=constants.USER_MODEL, on_delete=models.CASCADE, related_name='profile', verbose_name=_('user')
    )
    bio = models.TextField(verbose_name=_('biography'), null=False, blank=True)
    birthday = models.DateField(verbose_name=_('birthday'), null=True, blank=True)

    # Translating languages and sorting
    T_LANGUAGES = sorted(
        [(code, language) for code, language in settings.LANGUAGES],
        key=lambda x: x[1]
    )

    language = models.CharField(
        verbose_name=_('language'), choices=T_LANGUAGES, default=settings.LANGUAGE_CODE, max_length=10
    )
    web = models.URLField(verbose_name=_('website'), max_length=200, blank=True, null=False)
    image = models.ImageField(
        verbose_name=_('avatar'), upload_to=default_upload_to, blank=True, null=False
    )

    def get_menus(self):
        """
        Gets all user's menus by its permissions.
        """

        DynamicMenu = apps.get_model(constants.DYNAMIC_MENU)

        # Filtering by permissions
        user = self.user
        menus_pks = user.user_permissions.values_list('menus', flat=True)
        menus_pks = [menu for menu in menus_pks if menu is not None]

        menus = DynamicMenu.objects.filter(
            models.Q(pk__in=menus_pks) | models.Q(permissions_required__isnull=True)
        ).filter(
            menu_type=MenuTypes.MAIN_MENU
        )
        # Getting uniques
        menus = set(menus)

        # Filtering by staff required
        if not user.is_staff:
            menus = {menu for menu in menus if not menu.staff_required}

        return list(menus)
    menus = cached_property(get_menus, name='menus')

    def get_context_menus(self, request):
        DynamicMenu = apps.get_model(constants.DYNAMIC_MENU)

        menu_referrer = request.COOKIES.get('_auth_user_menu_referrer', None)
        if not menu_referrer or menu_referrer == 'None':  # Because of JavaScript
            return list()

        context_menus = DynamicMenu.objects.filter(
            parent_id=menu_referrer,
            menu_type=MenuTypes.CONTEXT_MENU
        )
        return list(context_menus)

    @property
    def age(self):
        rdelta = relativedelta(timezone.datetime.today().date(), self.birthday)
        return rdelta.years

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
