from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RoleplayConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'roleplay'
    verbose_name = _('Roleplay')
