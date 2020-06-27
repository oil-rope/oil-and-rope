from django.db import models
from django.utils.translation import gettext_lazy as _


class Actions(models.TextChoices):
    """
    Lists of actions internally supported by the ORM.
    """

    list = 'list', _('List')
    create = 'create', _('Create')
    delete = 'remove', _('Remove')
