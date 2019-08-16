from ckeditor.fields import RichTextField
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.conf.global_settings import LANGUAGES
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from core.models import TracingMixin


def user_directory_path(instance, filename: str) -> str:
    """
    Helper function to store images in `[...]/user_pk/filename`.

    Parameters
    ----------
    instance: :class:`models.Model`
        The Model instance to get the PrimaryKey.
    filename: :class:`str`
        The filename to store.
    """

    import pdb
    pdb.set_trace()

    # File will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.profile.user.pk, filename)


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

    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='profile', verbose_name=_('User'),)
    bio = RichTextField(_('Biography'), null=True, blank=True,)
    birthday = models.DateField(_('Birthday'), null=True, blank=True,)

    # Translating languages and sorting
    T_LANGUAGES = sorted([(code, _(language)) for code, language in LANGUAGES], key=lambda x: x[1])

    language = models.CharField(_('Language'), choices=T_LANGUAGES, default=settings.LANGUAGE_CODE, max_length=30,)
    alias = models.CharField(_('Alias'), max_length=30, blank=True, null=True,)
    web = models.URLField(_('Website'), max_length=200, blank=True, null=True)
    image = models.ImageField(_('Avatar'), upload_to=user_directory_path, blank=True, null=True)

    @property
    def age(self):
        rdelta = relativedelta(timezone.datetime.today().date(), self.birthday)
        return rdelta.years

    # Metadata
    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')
        ordering = ['user__first_name']

    def __str__(self):
        return 'Profile {}'.format(self.user.username)


@receiver(post_save, sender=User)
def create_profile_post_save_receiver(instance: User, **kwargs):
    """
    Creates a :class:`Profile` once a :class:`auth.User` is created.
    """

    if kwargs.get('created', False):
        Profile.objects.create(user=instance)
