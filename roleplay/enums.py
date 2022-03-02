from django.db import models
from django.utils.translation import gettext_lazy as _


class DomainTypes(models.IntegerChoices):
    DOMAIN = 0, _('domain').title()
    SUBDOMAIN = 1, _('subdomain').title()


class RoleplaySystems(models.IntegerChoices):
    PATHFINDER = 0, 'Pathfinder'
    DUNGEONS_AND_DRAGONS = 1, 'Dungeons & Dragons'


class SiteTypes(models.IntegerChoices):
    HOUSE = 0, _('house').title()
    TOWN = 1, _('town').title()
    VILLAGE = 2, _('village').title()
    CITY = 3, _('city').title()
    METROPOLIS = 4, _('metropolis').title()
    FOREST = 5, _('forest').title()
    HILLS = 6, _('hills').title()
    MOUNTAINS = 7, _('mountains').title()
    MINES = 8, _('mines').title()
    RIVER = 9, _('river').title()
    SEA = 10, _('sea').title()
    DESERT = 11, _('desert').title()
    TUNDRA = 12, _('tundra').title()
    UNUSUAL = 13, _('unusual').title()
    ISLAND = 14, _('island').title()
    COUNTRY = 15, _('country').title()
    CONTINENT = 16, _('continent').title()
    WORLD = 17, _('world').title()
    OCEAN = 18, _('ocean').title()


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
