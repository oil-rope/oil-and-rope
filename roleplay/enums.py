from django.db import models
from django.utils.translation import gettext_lazy as _


class DomainTypes(models.IntegerChoices):
    DOMAIN = 0, _('Domain')
    SUBDOMAIN = 1, _('Subdomain')


class SiteTypes(models.IntegerChoices):
    HOUSE = 0, _('House')
    TOWN = 1, _('Town')
    VILLAGE = 2, _('Village')
    CITY = 3, _('City')
    METROPOLIS = 4, _('Metropolis')
    FOREST = 5, _('Forest')
    HILLS = 6, _('Hills')
    MOUNTAINS = 7, _('Mountains')
    MINES = 8, _('Mines')
    RIVER = 9, _('River')
    SEA = 10, _('Sea')
    DESERT = 11, _('Desert')
    TUNDRA = 12, _('Tundra')
    UNUSUAL = 13, _('Unusual')
    ISLAND = 14, _('Island')
    COUNTRY = 15, _('Country')
    CONTINENT = 16, _('Continent')
    WORLD = 17, _('World')
