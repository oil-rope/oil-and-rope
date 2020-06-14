from django.db import models
from django.utils.translation import gettext_lazy as _


class MenuTypes(models.IntegerChoices):
    MAIN_MENU = 0, _('Standard menu')
    CONTEXT_MENU = 1, _('Context menu')
