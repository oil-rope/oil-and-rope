from django.db import models
from django.utils.translation import gettext_lazy as _


class MenuTypes(models.IntegerChoices):
    MAIN_MENU = 0, _('standard menu').title()
    CONTEXT_MENU = 1, _('context menu').title()
