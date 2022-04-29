from django.db import models
from django.utils.translation import gettext_lazy as _


class DomainTypes(models.IntegerChoices):
    DOMAIN = 0, _('domain')
    SUBDOMAIN = 1, _('subdomain')


class RoleplaySystems(models.IntegerChoices):
    PATHFINDER_1 = 0, 'Pathfinder 1e'
    DUNGEONS_AND_DRAGONS_35 = 1, 'Dungeons & Dragons 3.5'


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
    SiteTypes.HOUSE: 'ic-home',
    SiteTypes.TOWN: 'ic-town',
    SiteTypes.VILLAGE: 'ic-village',
    SiteTypes.CITY: 'ic-city',
    SiteTypes.METROPOLIS: 'ic-metropolis',
    SiteTypes.FOREST: 'ic-forest',
    SiteTypes.HILLS: 'ic-hills',
    SiteTypes.MOUNTAINS: 'ic-mountain',
    SiteTypes.MINES: 'ic-mines',
    SiteTypes.RIVER: 'ic-river',
    SiteTypes.SEA: 'ic-sea',
    SiteTypes.DESERT: 'ic-desert',
    SiteTypes.TUNDRA: 'ic-tundra',
    SiteTypes.UNUSUAL: 'ic-unusual',
    SiteTypes.ISLAND: 'ic-island',
    SiteTypes.COUNTRY: 'ic-flag',
    SiteTypes.CONTINENT: 'ic-continent',
    SiteTypes.WORLD: 'ic-world'
}
