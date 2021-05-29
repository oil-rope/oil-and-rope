from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DynamicMenuConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'dynamic_menu'
    verbose_name = _('Dynamic Menu')
