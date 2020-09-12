from ckeditor.fields import RichTextField
from dateutil.relativedelta import relativedelta
from django.apps import apps
from django.conf import settings
from django.conf.global_settings import LANGUAGES
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from common.constants import models as constants
from core.models import TracingMixin
from dynamic_menu.enums import MenuTypes


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

    # File will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.user.pk, filename)


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
    bio = RichTextField(verbose_name=_('Biography'), null=True, blank=True,)
    birthday = models.DateField(verbose_name=_('Birthday'), null=True, blank=True,)

    # Translating languages and sorting
    T_LANGUAGES = sorted([(code, _(language))
                          for code, language in LANGUAGES], key=lambda x: x[1])

    language = models.CharField(verbose_name=_('Language'), choices=T_LANGUAGES,
                                default=settings.LANGUAGE_CODE, max_length=30,)
    alias = models.CharField(verbose_name=_('Alias'), max_length=30, blank=True, null=True,)
    web = models.URLField(verbose_name=_('Website'), max_length=200, blank=True, null=True)
    image = models.ImageField(verbose_name=_('Avatar'), upload_to=user_directory_path,
                              blank=True, null=True)

    def get_menus(self):
        """
        Gets all user's menus by its permissions.
        """

        DynamicMenu = apps.get_model(constants.DYNAMIC_MENU)
        Permission = apps.get_model(constants.PERMISSION_MODEL)

        # Filtering by permissions
        user = self.user
        if user.is_superuser:
            menus_pks = Permission.objects.values_list('menus', flat=True)
        else:
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
        # Filtering by superuser
        if not user.is_superuser:
            menus = {menu for menu in menus if not menu.superuser_required}

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
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')
        ordering = ['user__username', 'user__first_name']

    def __str__(self):
        return 'Profile {}'.format(self.user.username)


@receiver(post_save, sender=User)
def create_profile_post_save_receiver(instance: User, **kwargs):
    """
    Creates a :class:`Profile` once a :class:`auth.User` is created.
    """

    if kwargs.get('created', False):
        Profile.objects.create(user=instance)
