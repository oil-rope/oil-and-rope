from django.db import models
from django.utils.translation import gettext_lazy as _


class AbilitiesEnum(models.TextChoices):
    STR = 'strength', _('strength')
    DEX = 'dexterity', _('dexterity')
    CON = 'constitution', _('constitution')
    INT = 'intelligence', _('intelligence')
    WIS = 'wisdom', _('wisdom')
    CHA = 'charisma', _('charisma')
