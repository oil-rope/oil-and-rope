from django.db import models
from mptt.models import TreeManager


class DomainManager(models.Manager):

    def subdomains(self):
        return super().get_queryset().filter(domain_type=self.model.SUBDOMAIN)

    def domains(self):
        return super().get_queryset().filter(domain_type=self.model.DOMAIN)


class PlaceManager(TreeManager):

    def houses(self):
        return super().get_queryset().filter(site_type=self.model.HOUSE)

    def towns(self):
        return super().get_queryset().filter(site_type=self.model.TOWN)

    def villages(self):
        return super().get_queryset().filter(site_type=self.model.VILLAGE)

    def cities(self):
        return super().get_queryset().filter(site_type=self.model.CITY)

    def metropolis(self):
        return super().get_queryset().filter(site_type=self.model.METROPOLIS)

    def forests(self):
        return super().get_queryset().filter(site_type=self.model.FOREST)

    def hills(self):
        return super().get_queryset().filter(site_type=self.model.HILLS)

    def mountains(self):
        return super().get_queryset().filter(site_type=self.model.MOUNTAINS)

    def mines(self):
        return super().get_queryset().filter(site_type=self.model.MINES)

    def rivers(self):
        return super().get_queryset().filter(site_type=self.model.RIVER)

    def seas(self):
        return super().get_queryset().filter(site_type=self.model.SEA)

    def deserts(self):
        return super().get_queryset().filter(site_type=self.model.DESERT)

    def tundras(self):
        return super().get_queryset().filter(site_type=self.model.TUNDRA)

    def unusuals(self):
        return super().get_queryset().filter(site_type=self.model.UNUSUAL)

    def islands(self):
        return super().get_queryset().filter(site_type=self.model.ISLAND)

    def countries(self):
        return super().get_queryset().filter(site_type=self.model.COUNTRY)

    def continents(self):
        return super().get_queryset().filter(site_type=self.model.CONTINENT)

    def worlds(self):
        return super().get_queryset().filter(site_type=self.model.WORLD)
