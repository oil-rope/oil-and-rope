from django.contrib.auth import get_user_model
from django.db import models
from mptt.models import TreeManager

from .enums import DomainTypes


class DomainManager(models.Manager):

    def subdomains(self):
        return super().get_queryset().filter(domain_type=DomainTypes.SUBDOMAIN)

    def domains(self):
        return super().get_queryset().filter(domain_type=DomainTypes.DOMAIN)


class PlaceManager(TreeManager):

    def user_places(self, user):
        """
        :param user: Either a user ID or User instance.
        :return: All the places related to that user.
        """

        if isinstance(user, get_user_model()):
            user = user.id
        return super().get_queryset().filter(user_id=user)

    def community_places(self):
        """
        Union places without user (community).

        :return: A QuerySet with all community_places.
        """

        return super().get_queryset().filter(user__isnull=True)

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
