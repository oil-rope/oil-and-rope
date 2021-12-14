from django.db import models
from django.utils.translation import gettext_lazy as _


class DomainTypes(models.IntegerChoices):
    DOMAIN = 0, _('domain')
    SUBDOMAIN = 1, _('subdomain')


class RoleplaySystems(models.IntegerChoices):
    PATHFINDER = 0, 'Pathfinder'
    DUNGEONS_AND_DRAGONS = 1, 'Dungeons & Dragons'


class SiteTypes(models.IntegerChoices):
    HOUSE = 0, _('house')
    TOWN = 1, _('town')
    VILLAGE = 2, _('village')
    CITY = 3, _('city')
    METROPOLIS = 4, _('metropolis')
    FOREST = 5, _('forest')
    HILLS = 6, _('hills')
    MOUNTAINS = 7, _('mountains')
    MINES = 8, _('mines')
    RIVER = 9, _('river')
    SEA = 10, _('sea')
    DESERT = 11, _('desert')
    TUNDRA = 12, _('tundra')
    UNUSUAL = 13, _('unusual')
    ISLAND = 14, _('island')
    COUNTRY = 15, _('country')
    CONTINENT = 16, _('continent')
    WORLD = 17, _('world')
    OCEAN = 18, _('ocean')


ICON_RESOLVERS = {
    SiteTypes.HOUSE: '',
    SiteTypes.TOWN: 'ic-town',
    SiteTypes.VILLAGE: '',
    SiteTypes.CITY: 'ic-city',
    SiteTypes.METROPOLIS: '',
    SiteTypes.FOREST: '',
    SiteTypes.HILLS: '',
    SiteTypes.MOUNTAINS: '',
    SiteTypes.MINES: '',
    SiteTypes.RIVER: '',
    SiteTypes.SEA: '',
    SiteTypes.DESERT: '',
    SiteTypes.TUNDRA: '',
    SiteTypes.UNUSUAL: '',
    SiteTypes.ISLAND: '',
    SiteTypes.COUNTRY: 'ic-flag',
    SiteTypes.CONTINENT: '',
    SiteTypes.WORLD: 'ic-world'
}
