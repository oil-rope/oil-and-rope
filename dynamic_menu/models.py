import logging

from django.apps import apps
from django.db import models
from django.shortcuts import reverse
from django.urls.exceptions import NoReverseMatch
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from common.constants import models as constants
from core.models import TracingMixin

from . import managers
from .enums import MenuTypes

PERMISSION_CLASS = 'auth.Permission'
MODEL_MANAGER_CLASS = 'contenttypes.ContentType'


def dynamic_menu_path(instance: models.Model, filename: str) -> str:
    """
    Sets the storage to save the file dynamically.
    """

    return 'dynamic_menu/dynamic_menu/{0}/{1}'.format(instance.pk, filename)


class DynamicMenu(MPTTModel, TracingMixin):
    """
    This model manages the menu so it can be created dynamically.
    Menus are managed by TreeStructure, that means you can set multiple menus and its
    options depending each other.

    Params
    ------
    name: :class:`str`
        Menu name display.
    description: Optional[:class:`str`]
        About this section of the menu.
    prepended_text: Optional[:class:`str`]
        Text, symbols or plain HTML to display before the menu's name.
        Prepended text is marked as 'safe' son plain HTML will be rendered as
        HTML.
    appended_text: Optional[:class:`str`]
        As well a `preprende_text`, text, symbols or plain HTML will be displayed
        after menu's name.
        Appended text is marked as 'safe' son plain HTML will be rendered as
        HTML.
    parent: Optional[:class:`DynamicMenu`]
        The parent menu if this section comes from another register.
    url_resolver: Optional[:class:`str`]
        Since we are configuring a menu section, Django's url resolve can be passed and
        automatically used.
    extra_urls_args: Optional[:class:`str`]
        Extra information or params to add to URL.
        >>> # Whatever PKs uses
        >>> obj = DynamicMenu.objects.get(pk=1)
        >>> param = '?extra_param=true'
        >>> obj.extra_url_args = param
        >>> obj.save()
        >>> # Assuming 'url_resolver' returns '/en/'
        >>> obj.url
        '/en/?extra_param=true'
    order: Optional[:class:`int`]
        How menus should be displayed.
    permissions_required: List[Optional[:class:`auth.Permission`]]
        List of permissions needed to access this menu.
    staff_required: Optional[:class:`bool`]
        Declares if staff is required to access this section of the menu.
    superuser_required: Optional[:class:`bool`]
        Declares if superuser is required to access this section of the menu.
    icon: Optional[:class:`file`]
        Icon asociated to this section of the menu.
    related_models: Optional[List[:class:`models.Model`]]
        A model related to this section of the menu.
    menu_type: Optional[:class:`int`]
        Role for this menu.
        `MAIN_MENU` stands for a regular menu section.
        `CONTEXT_MENU` stands for specific options that can be displayed
        under certains circunstances.

    Attributes
    ----------
    url: :class:`str`
        Return the URL if exists for this menu.
    created_at: :class:`datetime.datetime`
        The date when the model was created.
    updated_at: :class:`datetime.datetime`
        Last time model was updated.
    """

    name = models.CharField(verbose_name=_('Name'), max_length=100)
    description = models.TextField(verbose_name=_('Description'), null=True, blank=True)
    prepended_text = models.CharField(verbose_name=_('Prepended Text'), max_length=50,
                                      null=True, blank=True)
    appended_text = models.CharField(verbose_name=_('Appended Text'), max_length=50,
                                     null=True, blank=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, related_name='menus',
                            null=True, blank=True, verbose_name=_('Parent Menu'))
    url_resolver = models.CharField(verbose_name=_('URL Resolver'), max_length=50,
                                    null=True, blank=True)
    extra_urls_args = models.CharField(verbose_name=_('Extra URL Parameters'), max_length=254,
                                       null=True, blank=True)
    order = models.PositiveSmallIntegerField(verbose_name=_('Order'), default=0)
    permissions_required = models.ManyToManyField(PERMISSION_CLASS, blank=True,
                                                  related_name='menus',
                                                  verbose_name=_('Permissions required'))
    staff_required = models.BooleanField(verbose_name=_('Staff Required'), default=False)
    superuser_required = models.BooleanField(verbose_name=_('SuperUser Required'),
                                             default=False)
    icon = models.FileField(verbose_name=_('Icon'), upload_to=dynamic_menu_path,
                            max_length=254, blank=True, null=True)
    related_models = models.ManyToManyField(MODEL_MANAGER_CLASS, verbose_name=_('Related Models'),
                                            related_name='menus', blank=True)

    menu_type = models.PositiveSmallIntegerField(verbose_name=_('Menu Type'), default=MenuTypes.MAIN_MENU,
                                                 choices=MenuTypes.choices)

    objects = managers.DynamicMenuManager()

    @property
    def url(self) -> str:
        """
        Returns the URL for this menu if exists.
        """

        # By default empty menu will have '#no-url'
        url = '#no-url'

        try:
            # Checking if resolver exists
            if self.url_resolver:
                url = reverse(self.url_resolver)
            # Checking for extra args
            if self.extra_urls_args:
                url += self.extra_urls_args
        except NoReverseMatch as ex:
            logging.warning('Resolver for \'%s\' may not exists.',
                            self.url_resolver)
            logging.error('%s', ex)
        finally:
            return url

    def _get_permissions(self) -> set:
        """
        Executes Query to get related permissions.
        """

        permissions = self.permissions_required.values_list(
            'content_type__app_label',
            'codename'
        )
        permissions = {f'{app_label}.{codename}' for app_label, codename in permissions}
        return permissions

    def _get_models(self) -> set:
        """
        Executes Query to get related models.
        """

        models = self.related_models.values_list(
            'app_label',
            'model'
        )
        models = {f'{app_label}.{codename.capitalize()}' for app_label, codename in models}
        return models

    def get_permissions(self) -> set:
        """
        Returns a set of permissions for this menu.
        """

        permissions = self._get_permissions()
        return permissions
    permissions = cached_property(get_permissions, name='permissions')

    def get_models(self) -> set:
        """
        Returns a set of models related to this menu.
        """

        models = self._get_models()
        return models
    models = cached_property(get_models, name='models')

    @property
    def display_menu_name(self):
        menu_str = ''

        # Adding prepended_text
        if self.prepended_text:
            menu_str = mark_safe(self.prepended_text) + '  '
        # Menu name
        menu_str += self.name
        # Adding appended_text
        if self.appended_text:
            menu_str += '  ' + mark_safe(self.appended_text)

        return menu_str

    def add_permissions(self, *objs):
        """
        Takes a list of perms either :class:`str` (`app_label.codename`) or :class:`auth.Permission` instance.
        """

        Permission = apps.get_model(constants.PERMISSION_MODEL)
        parsed_objs = []

        for obj in objs:
            if isinstance(obj, str):
                # Perms are parsed from 'app_label.perm'
                app_label, codename = obj.split('.', 1)
                parsed_objs.append(
                    Permission.objects.get(content_type__app_label=app_label, codename=codename)
                )
            else:
                parsed_objs.append(obj)

        self.permissions_required.add(*parsed_objs)

    def add_models(self, *objs):
        """
        Takes a list of model either in :class:`str` (`app_label.model`), :class:`models.Model` subclass
        or :class:`contenttypes.ContentType` instance format.
        """

        ContentType = apps.get_model(constants.CONTENT_TYPE_MODEL)
        parsed_objs = []

        for obj in objs:
            if isinstance(obj, str):
                # Models are parsed from 'app_label.model'
                app_label, model = obj.lower().split('.', 1)
                parsed_objs.append(
                    ContentType.objects.get(app_label=app_label, model=model)
                )
            elif isinstance(obj, ContentType):
                parsed_objs.append(obj)
            elif hasattr(obj, '_meta') and issubclass(obj._meta.model, models.Model):
                app_label, model = obj._meta.label.lower().split('.', 1)
                parsed_objs.append(
                    ContentType.objects.get(app_label=app_label, model=model)
                )

        self.related_models.add(*parsed_objs)

    class Meta:
        verbose_name = _('Dynamic Menu')
        verbose_name_plural = _('Dynamic Menus')

    class MPTTMeta:
        order_insertion_by = ['order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return self.url
