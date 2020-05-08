from django.db import models


class DomainManager(models.Manager):

    def subdomains(self):
        """
        :return: All entries that are subdomains.
        """

        return super().get_queryset().filter(domain_type=self.model.SUBDOMAIN)

    def domains(self):
        """
        :return: All entries that are domains.
        """

        return super().get_queryset().filter(domain_type=self.model.DOMAIN)
