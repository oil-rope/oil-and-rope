from django.contrib.auth import get_user_model
from django.db import models
from mptt.models import TreeManager

from .enums import DomainTypes, SiteTypes


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

    def own_places(self, user):
        """
        Return places where user is owner.
        """

        if isinstance(user, get_user_model()):
            user = user.id
        return super().get_queryset().filter(owner_id=user)

    def community_places(self):
        """
        Union places without user (community).

        :return: A QuerySet with all community_places.
        """

        return super().get_queryset().filter(user__isnull=True)

    def houses(self):
        return super().get_queryset().filter(site_type=SiteTypes.HOUSE)

    def towns(self):
        return super().get_queryset().filter(site_type=SiteTypes.TOWN)

    def villages(self):
        return super().get_queryset().filter(site_type=SiteTypes.VILLAGE)

    def cities(self):
        return super().get_queryset().filter(site_type=SiteTypes.CITY)

    def metropolis(self):
        return super().get_queryset().filter(site_type=SiteTypes.METROPOLIS)

    def forests(self):
        return super().get_queryset().filter(site_type=SiteTypes.FOREST)

    def hills(self):
        return super().get_queryset().filter(site_type=SiteTypes.HILLS)

    def mountains(self):
        return super().get_queryset().filter(site_type=SiteTypes.MOUNTAINS)

    def mines(self):
        return super().get_queryset().filter(site_type=SiteTypes.MINES)

    def rivers(self):
        return super().get_queryset().filter(site_type=SiteTypes.RIVER)

    def seas(self):
        return super().get_queryset().filter(site_type=SiteTypes.SEA)

    def deserts(self):
        return super().get_queryset().filter(site_type=SiteTypes.DESERT)

    def tundras(self):
        return super().get_queryset().filter(site_type=SiteTypes.TUNDRA)

    def unusuals(self):
        return super().get_queryset().filter(site_type=SiteTypes.UNUSUAL)

    def islands(self):
        return super().get_queryset().filter(site_type=SiteTypes.ISLAND)

    def countries(self):
        return super().get_queryset().filter(site_type=SiteTypes.COUNTRY)

    def continents(self):
        return super().get_queryset().filter(site_type=SiteTypes.CONTINENT)

    def worlds(self):
        return super().get_queryset().filter(site_type=SiteTypes.WORLD)
