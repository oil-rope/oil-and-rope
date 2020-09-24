from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

from common.constants import models as constants
from common.files.upload import default_upload_to
from common.validators import validate_file_size
from core.models import TracingMixin
from roleplay.enums import RoleplaySystems

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

    def images(self):
        images = []
        if self.image:
            images.extend([self.image])
        images.extend([obj.image for obj in self.get_descendants().filter(image__isnull=False) if obj.image])
        return images

    def resolve_icon(self):
        return '<span class="{}"></span>'.format(self.ICON_RESOLVERS.get(self.site_type, ''))

    def get_houses(self):
        return self.get_descendants().filter(site_type=SiteTypes.HOUSE)

    def get_towns(self):
        return self.get_descendants().filter(site_type=SiteTypes.TOWN)

    def get_villages(self):
        return self.get_descendants().filter(site_type=SiteTypes.VILLAGE)

    def get_cities(self):
        return self.get_descendants().filter(site_type=SiteTypes.CITY)

    def get_metropolis(self):
        return self.get_descendants().filter(site_type=SiteTypes.METROPOLIS)

    def get_forests(self):
        return self.get_descendants().filter(site_type=SiteTypes.FOREST)

    def get_hills(self):
        return self.get_descendants().filter(site_type=SiteTypes.HILLS)

    def get_mountains(self):
        return self.get_descendants().filter(site_type=SiteTypes.MOUNTAINS)

    def get_mines(self):
        return self.get_descendants().filter(site_type=SiteTypes.MINES)

    def get_rivers(self):
        return self.get_descendants().filter(site_type=SiteTypes.RIVER)

    def get_seas(self):
        return self.get_descendants().filter(site_type=SiteTypes.SEA)

    def get_deserts(self):
        return self.get_descendants().filter(site_type=SiteTypes.DESERT)

    def get_tundras(self):
        return self.get_descendants().filter(site_type=SiteTypes.TUNDRA)

    def get_unusuals(self):
        return self.get_descendants().filter(site_type=SiteTypes.UNUSUAL)

    def get_islands(self):
        return self.get_descendants().filter(site_type=SiteTypes.ISLAND)

    def get_countries(self):
        return self.get_descendants().filter(site_type=SiteTypes.COUNTRY)

    def get_continents(self):
        return self.get_descendants().filter(site_type=SiteTypes.CONTINENT)

    def get_worlds(self):
        return self.get_descendants().filter(site_type=SiteTypes.WORLD)

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


class Session(TracingMixin):
    """
    This model manages sessions playing by the users.

    Parameters
    ----------
    name: :class:`str`
        Name of the session.
    players: List[:class:`User`]
        Players in session.
    chat: :class:`Chat`
        Caht used for this session.
    """

    name = models.CharField(verbose_name=_('Name'), max_length=100)
    description = models.TextField(verbose_name=_('Description'), null=True, blank=True)
    players = models.ManyToManyField(get_user_model(), verbose_name=_('Players'), related_name='session_set')
    chat = models.ForeignKey(
        to=constants.CHAT_MODEL, verbose_name=_('Chat'), on_delete=models.CASCADE,
        related_name='session_set', db_index=True, blank=True
    )
    next_game = models.DateTimeField(
        verbose_name=_('Next session'), auto_now=False, auto_now_add=False, null=True, blank=True
    )
    system = models.PositiveSmallIntegerField(verbose_name=_('System'), choices=RoleplaySystems.choices)
    game_master = models.ForeignKey(
        to=constants.USER_MODEL, verbose_name=_('GameMaster'), on_delete=models.CASCADE,
        related_name='gm_session_set', db_index=True
    )
    world = models.ForeignKey(
        to=constants.PLACE_MODEL, verbose_name=_('World'), on_delete=models.CASCADE,
        related_name='session_set', db_index=True, limit_choices_to={'site_type': SiteTypes.WORLD}
    )

    class Meta:
        verbose_name = _('Session')
        verbose_name_plural = _('Sessions')
        ordering = ['-entry_created_at', 'name']

    def clean(self):
        # Don't allow non Worlds to be world
        if self.world.site_type != SiteTypes.WORLD:
            msg = _('World must be a world')
            raise ValidationError({'world': f'{msg}.'})

    def save(self, *args, **kwargs):
        Chat = apps.get_model(constants.CHAT_MODEL)
        self.full_clean()

        try:
            self.chat
        except Session.chat.RelatedObjectDoesNotExist:
            formatted_date = timezone.now().strftime('%Y%m%d_%H%M%S')
            self.chat = Chat.objects.create(
                name=f'{self.name}_{formatted_date}'
            )
        finally:
            super().save(*args, **kwargs)

    def __str__(self):
        created_at = self.entry_created_at.strftime('%Y-%m-%d')
        return f'{self.name} ({created_at})'
