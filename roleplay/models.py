from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

from common.constants import models as constants
from common.files.upload import default_upload_to
from common.validators import validate_file_size, validate_music_file
from core.models import TracingMixin

from . import managers
from .enums import ICON_RESOLVERS, DomainTypes, SiteTypes


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

    name = models.CharField(verbose_name=_('Name'), max_length=25, null=False, blank=False)
    description = models.TextField(verbose_name=_('Description'), null=True, blank=True)
    domain_type = models.PositiveSmallIntegerField(verbose_name=_('Domain type'), choices=DomainTypes.choices,
                                                   default=DomainTypes.DOMAIN, null=False, blank=False)
    image = models.ImageField(verbose_name=_('Image'), upload_to=default_upload_to, null=True, blank=True)

    objects = managers.DomainManager()

    @property
    def is_domain(self):
        return self.domain_type == DomainTypes.DOMAIN

    @property
    def is_subdomain(self):
        return self.domain_type == DomainTypes.SUBDOMAIN

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

    ICON_RESOLVERS = ICON_RESOLVERS

    name = models.CharField(verbose_name=_('Name'), max_length=100, null=False, blank=False)
    description = models.TextField(verbose_name=_('Description'), null=True, blank=True)
    site_type = models.PositiveSmallIntegerField(verbose_name=_('Site type'), choices=SiteTypes.choices,
                                                 default=SiteTypes.TOWN, null=False, blank=False)
    image = models.ImageField(verbose_name=_('Image'), upload_to=default_upload_to, null=True, blank=True,
                              validators=[validate_file_size])
    parent_site = TreeForeignKey('self', verbose_name=_('Parent site'), on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='children_sites', db_index=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='places', verbose_name=_('User'),
                             blank=True, null=True, db_index=True)
    owner = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, related_name='places_owned',
                              verbose_name=_('Owner'), blank=True, null=True, db_index=True)

    objects = managers.PlaceManager()

    @cached_property
    def images(self):
        images = []
        if self.image:
            images.extend([self.image])
        images.extend([obj.image for obj in self.get_descendants().filter(image__isnull=False) if obj.image])
        return images

    def resolve_icon(self):
        return '<span class="{}"></span>'.format(self.ICON_RESOLVERS.get(self.site_type, ''))

    def get_houses(self):
        houses = self.get_descendants().filter(site_type=SiteTypes.HOUSE)
        houses = list(houses)
        return houses
    houses = cached_property(get_houses, name='houses')

    def get_towns(self):
        towns = self.get_descendants().filter(site_type=SiteTypes.TOWN)
        towns = list(towns)
        return towns
    towns = cached_property(get_towns, name='towns')

    def get_villages(self):
        villages = self.get_descendants().filter(site_type=SiteTypes.VILLAGE)
        villages = list(villages)
        return villages
    villages = cached_property(get_villages, name='villages')

    def get_cities(self):
        cities = self.get_descendants().filter(site_type=SiteTypes.CITY)
        cities = list(cities)
        return cities
    cities = cached_property(get_cities, name='cities')

    def get_metropolis(self):
        metropolis = self.get_descendants().filter(site_type=SiteTypes.METROPOLIS)
        metropolis = list(metropolis)
        return metropolis
    metropolis = cached_property(get_metropolis, name='metropolis')

    def get_forests(self):
        forests = self.get_descendants().filter(site_type=SiteTypes.FOREST)
        forests = list(forests)
        return forests
    forests = cached_property(get_forests, name='forests')

    def get_hills(self):
        hills = self.get_descendants().filter(site_type=SiteTypes.HILLS)
        hills = list(hills)
        return hills
    hills = cached_property(get_hills, name='hills')

    def get_mountains(self):
        mountains = self.get_descendants().filter(site_type=SiteTypes.MOUNTAINS)
        mountains = list(mountains)
        return mountains
    mountains = cached_property(get_mountains, name='mountains')

    def get_mines(self):
        mines = self.get_descendants().filter(site_type=SiteTypes.MINES)
        mines = list(mines)
        return mines
    mines = cached_property(get_mines, name='mines')

    def get_rivers(self):
        rivers = self.get_descendants().filter(site_type=SiteTypes.RIVER)
        rivers = list(rivers)
        return rivers
    rivers = cached_property(get_rivers, name='rivers')

    def get_seas(self):
        seas = self.get_descendants().filter(site_type=SiteTypes.SEA)
        seas = list(seas)
        return seas
    seas = cached_property(get_seas, name='seas')

    def get_deserts(self):
        deserts = self.get_descendants().filter(site_type=SiteTypes.DESERT)
        deserts = list(deserts)
        return deserts
    deserts = cached_property(get_deserts, name='deserts')

    def get_tundras(self):
        tundras = self.get_descendants().filter(site_type=SiteTypes.TUNDRA)
        tundras = list(tundras)
        return tundras
    tundras = cached_property(get_tundras, name='tundras')

    def get_unusuals(self):
        unusuals = self.get_descendants().filter(site_type=SiteTypes.UNUSUAL)
        unusuals = list(unusuals)
        return unusuals
    unusuals = cached_property(get_unusuals, name='unusuals')

    def get_islands(self):
        islands = self.get_descendants().filter(site_type=SiteTypes.ISLAND)
        islands = list(islands)
        return islands
    islands = cached_property(get_islands, name='islands')

    def get_countries(self):
        countries = self.get_descendants().filter(site_type=SiteTypes.COUNTRY)
        countries = list(countries)
        return countries
    countries = cached_property(get_countries, name='countries')

    def get_continents(self):
        continents = self.get_descendants().filter(site_type=SiteTypes.CONTINENT)
        continents = list(continents)
        return continents
    continents = cached_property(get_continents, name='continents')

    def get_worlds(self):
        worlds = self.get_descendants().filter(site_type=SiteTypes.WORLD)
        worlds = list(worlds)
        return worlds
    worlds = cached_property(get_worlds, name='worlds')

    @property
    def is_house(self):
        return self.site_type == SiteTypes.HOUSE

    @property
    def is_town(self):
        return self.site_type == SiteTypes.TOWN

    @property
    def is_village(self):
        return self.site_type == SiteTypes.VILLAGE

    @property
    def is_city(self):
        return self.site_type == SiteTypes.CITY

    @property
    def is_metropolis(self):
        return self.site_type == SiteTypes.METROPOLIS

    @property
    def is_forest(self):
        return self.site_type == SiteTypes.FOREST

    @property
    def is_hills(self):
        return self.site_type == SiteTypes.HILLS

    @property
    def is_mountains(self):
        return self.site_type == SiteTypes.MOUNTAINS

    @property
    def is_mines(self):
        return self.site_type == SiteTypes.MINES

    @property
    def is_river(self):
        return self.site_type == SiteTypes.RIVER

    @property
    def is_sea(self):
        return self.site_type == SiteTypes.SEA

    @property
    def is_desert(self):
        return self.site_type == SiteTypes.DESERT

    @property
    def is_tundra(self):
        return self.site_type == SiteTypes.TUNDRA

    @property
    def is_unusual(self):
        return self.site_type == SiteTypes.UNUSUAL

    @property
    def is_island(self):
        return self.site_type == SiteTypes.ISLAND

    @property
    def is_country(self):
        return self.site_type == SiteTypes.COUNTRY

    @property
    def is_continent(self):
        return self.site_type == SiteTypes.CONTINENT

    @property
    def is_world(self):
        return self.site_type == SiteTypes.WORLD

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


class Race(TracingMixin):
    """
    Model to manage Races.

    Parameters
    ----------
    name: :class:`str`
        Name of the race.
    description: :class:`str`
        About the creature.
    strength: :class:`int`
        Modifier for strength.
    dexterity: :class:`int`
        Modifier for dexterity.
    constitution: :class:`int`
        Modifier for constitution.
    intelligence: :class:`int`
        Modifier for intelligence.
    wisdom: :class:`int`
        Modifier for wisdom.
    charisma: :class:`int`
        Modfier for charisma.
    affected_by_armor: :class:`boolean`
        Declares if this race is affected by any penalty that armor can give.
    image: :class:`file`
        Image for the race.
    users: :class:`User`
        Users that have this race.
    """

    name = models.CharField(verbose_name=_('Name'), max_length=50)
    description = models.TextField(verbose_name=_('Description'), null=True, blank=True)
    strength = models.SmallIntegerField(verbose_name=_('Strength'), default=0)
    dexterity = models.SmallIntegerField(verbose_name=_('Dexterity'), default=0)
    constitution = models.SmallIntegerField(verbose_name=_('Constitution'), default=0)
    intelligence = models.SmallIntegerField(verbose_name=_('Intelligence'), default=0)
    wisdom = models.SmallIntegerField(verbose_name=_('Wisdom'), default=0)
    charisma = models.SmallIntegerField(verbose_name=_('Charisma'), default=0)
    affected_by_armor = models.BooleanField(verbose_name=_('Affected by armor'), default=True,
                                            help_text=_('Declares if this race is affected by armor penalties'))
    image = models.ImageField(verbose_name=_('Image'), upload_to=default_upload_to, validators=[validate_file_size],
                              null=True, blank=True)
    users = models.ManyToManyField(verbose_name=_('Users'), to=constants.USER_MODEL, related_name='race_set',
                                   db_index=True, through=constants.USER_RACE_RELATION)

    @property
    def owners(self):
        qs = self.users.filter(m2m_race_set__is_owner=True)
        return qs

    def add_owners(self, *users):
        # Getting RaceUser model
        model = apps.get_model(constants.USER_RACE_RELATION)
        new_entries = []
        for user in users:
            entry = model(user=user, race=self, is_owner=True)
            new_entries.append(entry.save())
        return model.objects.filter(pk__in=new_entries)

    class Meta:
        verbose_name = _('Race')
        verbose_name_plural = _('Races')
        ordering = ['-entry_created_at', 'name']

    def __str__(self):
        return f'{self.name} [{self.pk}]'


class RaceUser(TracingMixin):
    """
    This class manage M2M for :class:`Race` and :class:`User`.

    Parameters
    ----------
    user: :class:`User`
        Related user.
    race: :class:`Race`
        Related race.
    is_owner: :class:`boolean`
        Declares if the related user is owner.
    """

    user = models.ForeignKey(verbose_name=_('User'), to=constants.USER_MODEL, related_name='m2m_race_set',
                             on_delete=models.CASCADE, db_index=True)
    race = models.ForeignKey(verbose_name=_('Race'), to=constants.RACE_MODEL, related_name='m2m_race_set',
                             on_delete=models.CASCADE, db_index=True)
    is_owner = models.BooleanField(verbose_name=_('Ownership'), default=False)

    def __str__(self):
        return f'{self.user.username} <-> {self.race.name}'


class Music(TracingMixin):
    """
    This class manages the music for the game.

    Parameters
    ----------
    title: :class:`str`
        The title of the song.
    description: Optional[:class:`str`]
        Description for the song if needed.
    file: :class:`file`
        The song uploaded.
    users: :class:`MusicUser`
        Users that have this song.
    """

    title = models.CharField(verbose_name=_('Title'), max_length=50)
    description = models.TextField(verbose_name=_('Description'), null=True, blank=True)
    file = models.FileField(verbose_name=_('File'), upload_to=default_upload_to,
                            validators=[validate_file_size, validate_music_file])
    users = models.ManyToManyField(verbose_name=_('Users'), to=constants.USER_MODEL, related_name='music_set',
                                   db_index=True, through=constants.USER_MUSIC_RELATION)

    limit = models.Q(app_label='roleplay', model__in=['race', 'place'])
    # TODO: This should be posible to associate with everything
    content_type = models.ForeignKey(
        to=constants.CONTENT_TYPE_MODEL, verbose_name=_('Association'), limit_choices_to=limit,
        blank=True, null=True, on_delete=models.CASCADE, db_index=True
    )
    object_id = models.IntegerField(verbose_name=_('Identifier'), null=True, blank=True)
    association = GenericForeignKey(ct_field='content_type', fk_field='object_id')

    class Meta:
        verbose_name = _('Music')
        verbose_name_plural = _('Music')
        ordering = ['title', '-entry_created_at']

    def __str__(self):
        return f'{self.title}'


class MusicUser(TracingMixin):
    """
    This class manage M2M for :class:`Music` and :class:`User`.

    Parameters
    ----------
    user: :class:`User`
        Related user.
    music: :class:`Music`
        Related music.
    is_owner: :class:`boolean`
        Declares if the related user is owner.
    """

    user = models.ForeignKey(verbose_name=_('User'), to=constants.USER_MODEL, related_name='m2m_music_set',
                             on_delete=models.CASCADE, db_index=True)
    music = models.ForeignKey(verbose_name=_('Music'), to=constants.MUSIC_MODEL, related_name='m2m_music_set',
                              on_delete=models.CASCADE, db_index=True)
    is_owner = models.BooleanField(verbose_name=_('Ownership'), default=False)

    def __str__(self):
        return f'{self.user.username} <-> {self.music.title}'
