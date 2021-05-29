from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'chat'
    verbose_name = _('Chat')
