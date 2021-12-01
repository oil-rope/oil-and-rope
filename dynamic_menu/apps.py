from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DynamicMenuConfig(AppConfig):
    name = 'dynamic_menu'
    verbose_name = _('dynamic menu')
