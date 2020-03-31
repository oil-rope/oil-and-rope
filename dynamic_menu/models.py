import logging

from django.db import models
from django.shortcuts import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from core.models import TracingMixin

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
        >>> obj = DinamyMenu.objects.get(pk=pk)
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
    related_model = models.ManyToManyField(MODEL_MANAGER_CLASS, verbose_name=_("Related Model"),
                                           related_name='menus', blank=True)

    MAIN_MENU = 0
    CONTEXT_MENU = 1
    MENU_CHOICES = (
        (MAIN_MENU, _('Standard Menu')),
        (CONTEXT_MENU, _('Context Menu')),
    )

    menu_type = models.PositiveSmallIntegerField(verbose_name=_('Menu Type'), default=MAIN_MENU,
                                                 choices=MENU_CHOICES)

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
        except Exception as ex:
            logging.warning('Resolver for \'%s\' may not exists.',
                            self.url_resolver)
            logging.error('%s', ex)
        finally:
            return url

    class Meta:
        verbose_name = _("Dynamic Menu")
        verbose_name_plural = _("Dynamic Menus")

    def __str__(self):
        menu_str = ''

        # Adding prepended_text
        if self.prepended_text:
            menu_str = mark_safe(self.prepended_text)
        # Menu name
        menu_str += self.name
        # Adding appended_text
        if self.appended_text:
            menu_str += mark_safe(self.appended_text)

        return menu_str

    def get_absolute_url(self):
        return self.url
