from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

from common.files.upload import default_upload_to
from common.validators import validate_file_size
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
    image = models.ImageField(verbose_name=_('Image'), upload_to=default_upload_to, null=True, blank=True)

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


class Place(MPTTModel, TracingMixin):
    """
    Declares where did the creature grown, how it was, what does it belong to?
    Also used for declaring a World.

    Parameters
    ----------
    name: :class:`str`
        Name of the site.
    description: :class:`str`
        Description of the site.
    site_type: :class:`int`
        0 - House, 1 - Town, 2 - Village...
    image: :class:`str`
        Path to the image.
    parent_site: :class:`int`
       If the place is child of another Place, this is where it can be settled.
    user: :class:`auth.User`
        Declares this maps belongs to a user.
    owner: :class:`auth.User`
        The person who created this map.
    """

    HOUSE = 0
    TOWN = 1
    VILLAGE = 2
    CITY = 3
    METROPOLIS = 4
    FOREST = 5
    HILLS = 6
    MOUNTAINS = 7
    MINES = 8
    RIVER = 9
    SEA = 10
    DESERT = 11
    TUNDRA = 12
    UNUSUAL = 13
    ISLAND = 14
    COUNTRY = 15
    CONTINENT = 16
    WORLD = 17

    SITE_TYPES = (
        (HOUSE, _('House')),
        (TOWN, _('Town')),
        (VILLAGE, _('Village')),
        (CITY, _('City')),
        (METROPOLIS, _('Metropolis')),
        (FOREST, _('Forest')),
        (HILLS, _('Hills')),
        (MOUNTAINS, _('Mountains')),
        (MINES, _('Mines')),
        (RIVER, _('River')),
        (SEA, _('Sea')),
        (DESERT, _('Desert')),
        (TUNDRA, _('Tundra')),
        (UNUSUAL, _('Unusual')),
        (ISLAND, _('Island')),
        (COUNTRY, _('Country')),
        (CONTINENT, _('Continent')),
        (WORLD, _('World'))
    )

    ICON_RESOLVERS = {
        HOUSE: '',
        TOWN: 'ic-town',
        VILLAGE: '',
        CITY: 'ic-city',
        METROPOLIS: '',
        FOREST: '',
        HILLS: '',
        MOUNTAINS: '',
        MINES: '',
        RIVER: '',
        SEA: '',
        DESERT: '',
        TUNDRA: '',
        UNUSUAL: '',
        ISLAND: '',
        COUNTRY: 'ic-flag',
        CONTINENT: '',
        WORLD: 'ic-world'
    }

    name = models.CharField(verbose_name=_('Name'), max_length=100, null=False, blank=False)
    description = models.TextField(verbose_name=_('Description'), null=True, blank=True)
    site_type = models.PositiveSmallIntegerField(verbose_name=_('Site type'), choices=SITE_TYPES, default=TOWN,
                                                 null=False, blank=False)
    image = models.ImageField(verbose_name=_('Image'), upload_to=default_upload_to, null=True, blank=True,
                              validators=[validate_file_size])
    parent_site = TreeForeignKey('self', verbose_name=_('Parent site'), on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='children_sites', db_index=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='places', verbose_name=_('User'),
                             blank=True, null=True, db_index=True)
    owner = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, related_name='places_owned',
                              verbose_name=_('Owner'), blank=True, null=True, db_index=True)

    objects = managers.PlaceManager()

    def images(self):
        images = []
        if self.image:
            images.extend([self.image])
        images.extend([obj.image for obj in self.get_descendants().filter(image__isnull=False) if obj.image])
        return images

    def resolve_icon(self):
        return '<span class="{}"></span>'.format(self.ICON_RESOLVERS.get(self.site_type, ''))

    def get_houses(self):
        return self.get_descendants().filter(site_type=self.HOUSE)

    def get_towns(self):
        return self.get_descendants().filter(site_type=self.TOWN)

    def get_villages(self):
        return self.get_descendants().filter(site_type=self.VILLAGE)

    def get_cities(self):
        return self.get_descendants().filter(site_type=self.CITY)

    def get_metropolis(self):
        return self.get_descendants().filter(site_type=self.METROPOLIS)

    def get_forests(self):
        return self.get_descendants().filter(site_type=self.FOREST)

    def get_hills(self):
        return self.get_descendants().filter(site_type=self.HILLS)

    def get_mountains(self):
        return self.get_descendants().filter(site_type=self.MOUNTAINS)

    def get_mines(self):
        return self.get_descendants().filter(site_type=self.MINES)

    def get_rivers(self):
        return self.get_descendants().filter(site_type=self.RIVER)

    def get_seas(self):
        return self.get_descendants().filter(site_type=self.SEA)

    def get_deserts(self):
        return self.get_descendants().filter(site_type=self.DESERT)

    def get_tundras(self):
        return self.get_descendants().filter(site_type=self.TUNDRA)

    def get_unusuals(self):
        return self.get_descendants().filter(site_type=self.UNUSUAL)

    def get_islands(self):
        return self.get_descendants().filter(site_type=self.ISLAND)

    def get_countries(self):
        return self.get_descendants().filter(site_type=self.COUNTRY)

    def get_continents(self):
        return self.get_descendants().filter(site_type=self.CONTINENT)

    def get_worlds(self):
        return self.get_descendants().filter(site_type=self.WORLD)

    @property
    def is_house(self):
        return self.site_type == self.HOUSE

    @property
    def is_town(self):
        return self.site_type == self.TOWN

    @property
    def is_village(self):
        return self.site_type == self.VILLAGE

    @property
    def is_city(self):
        return self.site_type == self.CITY

    @property
    def is_metropolis(self):
        return self.site_type == self.METROPOLIS

    @property
    def is_forest(self):
        return self.site_type == self.FOREST

    @property
    def is_hills(self):
        return self.site_type == self.HILLS

    @property
    def is_mountains(self):
        return self.site_type == self.MOUNTAINS

    @property
    def is_mines(self):
        return self.site_type == self.MINES

    @property
    def is_river(self):
        return self.site_type == self.RIVER

    @property
    def is_sea(self):
        return self.site_type == self.SEA

    @property
    def is_desert(self):
        return self.site_type == self.DESERT

    @property
    def is_tundra(self):
        return self.site_type == self.TUNDRA

    @property
    def is_unusual(self):
        return self.site_type == self.UNUSUAL

    @property
    def is_island(self):
        return self.site_type == self.ISLAND

    @property
    def is_country(self):
        return self.site_type == self.COUNTRY

    @property
    def is_continent(self):
        return self.site_type == self.CONTINENT

    @property
    def is_world(self):
        return self.site_type == self.WORLD

    class MPTTMeta:
        parent_attr = 'parent_site'

    class Meta:
        verbose_name = _('Place')
        verbose_name_plural = _('Places')
        ordering = ['name', '-entry_created_at', '-entry_updated_at']

    def clean(self):
        if self.user and not self.owner:
            raise ValidationError({
                'user': _('A private world must have owner') + '.'
            })

    def save(self, *args, **kwargs):
        if self.user and not self.owner:
            raise IntegrityError(_('A private world must have owner') + '.')
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name
