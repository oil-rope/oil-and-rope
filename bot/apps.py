from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BotConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'bot'
    verbose_name = _('Bot')
