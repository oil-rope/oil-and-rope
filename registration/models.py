from ckeditor.fields import RichTextField
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.conf.global_settings import LANGUAGES
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.functional import keep_lazy
from django.utils.translation import gettext_lazy as _

from common.constants import models as constants
from common.files.upload import default_upload_to
from core.models import TracingMixin


class User(AbstractUser):
    email = models.EmailField(verbose_name=_('email address'), null=False, blank=False, unique=True)
    is_premium = models.BooleanField(verbose_name=_('premium user'), default=False)

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

    class Meta:
        db_table = 'auth_user'


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
    bio = RichTextField(verbose_name=_('biography'), null=True, blank=True)
    birthday = models.DateField(verbose_name=_('birthday'), null=True, blank=True)

    # Translating languages and sorting
    T_LANGUAGES = sorted(
        [(code, _(language)) for code, language in LANGUAGES],
        key=lambda x: x[1]
    )

    language = models.CharField(
        verbose_name=_('language'), choices=T_LANGUAGES, default=settings.LANGUAGE_CODE, max_length=30
    )
    alias = models.CharField(verbose_name=_('alias'), max_length=30, blank=True, null=True)
    web = models.URLField(verbose_name=_('website'), max_length=200, blank=True, null=True)
    image = models.ImageField(
        verbose_name=_('avatar'), upload_to=default_upload_to, blank=True, null=True
    )

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
    Creates a :class:`Profile` once a :class:`auth.User` is created.
    """

    if kwargs.get('created', False):
        Profile.objects.create(user=instance)
