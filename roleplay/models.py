from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.models import TracingMixin

from . import managers


class Domain(TracingMixin):
    """
    Declares domain and subdomain differentiated by type.

    Parameters
    ----------
    name: :class:`str`
        Name of the domain.
    description: :class:`str`
        Little description about what involves this domain.
    """

    DOMAIN = 0
    SUBDOMAIN = 1
    DOMAIN_TYPES = (
        (DOMAIN, _('Domain')),
        (SUBDOMAIN, _('Subdomain'))
    )

    name = models.CharField(verbose_name=_('Name'), max_length=25, null=False, blank=False)
    description = models.TextField(verbose_name=_('Description'), null=True, blank=True)
    domain_type = models.PositiveSmallIntegerField(verbose_name=_('Domain type'), choices=DOMAIN_TYPES, default=DOMAIN,
                                                   null=False, blank=False)

    objects = managers.DomainManager()

    @property
    def is_domain(self):
        return self.domain_type == self.DOMAIN

    @property
    def is_subdomain(self):
        return self.domain_type == self.SUBDOMAIN

    class Meta:
        verbose_name = _('Domain')
        verbose_name_plural = _('Domains')
        ordering = ['name', '-entry_created_at', '-entry_updated_at']

    def __str__(self):
        return self.name
