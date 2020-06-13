from django.db import models
from django.utils.translation import gettext_lazy as _


class DomainTypes(models.IntegerChoices):
    DOMAIN = 0, _('Domain')
    SUBDOMAIN = 1, _('Subdomain')
