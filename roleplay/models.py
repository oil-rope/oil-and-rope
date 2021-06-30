from django.apps import apps
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
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

    name = models.CharField(verbose_name=_('name'), max_length=25, null=False, blank=False)
    description = models.TextField(verbose_name=_('description'), null=True, blank=True)
    domain_type = models.PositiveSmallIntegerField(
        verbose_name=_('domain type'), choices=DomainTypes.choices, default=DomainTypes.DOMAIN, null=False, blank=False
    )
    image = models.ImageField(verbose_name=_('image'), upload_to=default_upload_to, null=True, blank=True)

    objects = managers.DomainManager()

    @property
    def is_domain(self):
        return self.domain_type == DomainTypes.DOMAIN

    @property
    def is_subdomain(self):
        return self.domain_type == DomainTypes.SUBDOMAIN

    class Meta:
        verbose_name = _('domain')
        verbose_name_plural = _('domains')
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

    name = models.CharField(verbose_name=_('name'), max_length=100, null=False, blank=False)
    description = models.TextField(verbose_name=_('description'), null=True, blank=True)
    site_type = models.PositiveSmallIntegerField(
        verbose_name=_('site type'), choices=SiteTypes.choices, default=SiteTypes.TOWN, null=False, blank=False
    )
    image = models.ImageField(
        verbose_name=_('image'), upload_to=default_upload_to, null=True, blank=True, validators=[validate_file_size]
    )
    parent_site = TreeForeignKey(
        to='self', verbose_name=_('parent site'), on_delete=models.CASCADE, null=True, blank=True,
        related_name='children_sites', db_index=True
    )
    user = models.ForeignKey(
        to=constants.USER_MODEL, on_delete=models.CASCADE, related_name='places', verbose_name=_('user'), blank=True,
        null=True, db_index=True
    )
    owner = models.ForeignKey(
        to=constants.USER_MODEL, on_delete=models.SET_NULL, related_name='places_owned', verbose_name=_('owner'),
        blank=True, null=True, db_index=True
    )

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
        verbose_name = _('place')
        verbose_name_plural = _('places')
        ordering = ['name', '-entry_created_at', '-entry_updated_at']

    def clean(self):
        if self.user and not self.owner:
            raise ValidationError({
                'user': _('a private world must have owner') + '.'
            })

    def save(self, *args, **kwargs):
        if self.user and not self.owner:
            raise IntegrityError(_('a private world must have owner') + '.')
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

    name = models.CharField(verbose_name=_('name'), max_length=50)
    description = models.TextField(verbose_name=_('description'), null=True, blank=True)
    strength = models.SmallIntegerField(verbose_name=_('strength'), default=0)
    dexterity = models.SmallIntegerField(verbose_name=_('dexterity'), default=0)
    constitution = models.SmallIntegerField(verbose_name=_('constitution'), default=0)
    intelligence = models.SmallIntegerField(verbose_name=_('intelligence'), default=0)
    wisdom = models.SmallIntegerField(verbose_name=_('wisdom'), default=0)
    charisma = models.SmallIntegerField(verbose_name=_('charisma'), default=0)
    affected_by_armor = models.BooleanField(
        verbose_name=_('affected by armor'), default=True,
        help_text=_('declares if this race is affected by armor penalties')
    )
    image = models.ImageField(
        verbose_name=_('image'), upload_to=default_upload_to, validators=[validate_file_size], null=True, blank=True
    )
    users = models.ManyToManyField(
        verbose_name=_('users'), to=constants.USER_MODEL, related_name='race_set', db_index=True,
        through=constants.USER_RACE_RELATION,
    )

    def get_owners(self):
        qs = self.users.filter(m2m_race_set__is_owner=True)
        return qs

    owners = cached_property(func=get_owners, name='owners')

    def add_owners(self, *users):
        # Getting RaceUser model
        model = apps.get_model(constants.USER_RACE_RELATION)
        new_entries = []
        for user in users:
            entry = model(user=user, race=self, is_owner=True)
            new_entries.append(entry.save())
        return model.objects.filter(pk__in=new_entries)

    class Meta:
        verbose_name = _('race')
        verbose_name_plural = _('races')
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

    user = models.ForeignKey(
        verbose_name=_('user'), to=constants.USER_MODEL, related_name='m2m_race_set', on_delete=models.CASCADE,
        db_index=True
    )
    race = models.ForeignKey(
        verbose_name=_('race'), to=constants.RACE_MODEL, related_name='m2m_race_set', on_delete=models.CASCADE,
        db_index=True
    )
    is_owner = models.BooleanField(verbose_name=_('ownership'), default=False)

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
        Chat used for this session.
    next_game: :class:`datetime.datetime`
        Next session's date.
    system: :class:`int`
        System used.
    game_master: :class:`auth.User`
        The GM of the session.
    world: :class:`roleplay.Place`
        The world where this session is played.
    """

    name = models.CharField(verbose_name=_('name'), max_length=100)
    description = models.TextField(verbose_name=_('description'), null=True, blank=True)
    players = models.ManyToManyField(
        to=constants.USER_MODEL, verbose_name=_('players'), related_name='session_set', related_query_name='session'
    )
    chat = models.ForeignKey(
        to=constants.CHAT_MODEL, verbose_name=_('chat'), on_delete=models.CASCADE,
        related_name='session_set', related_query_name='session', db_index=True, blank=True
    )
    next_game = models.DateTimeField(
        verbose_name=_('next session'), auto_now=False, auto_now_add=False, null=True, blank=True
    )
    system = models.PositiveSmallIntegerField(verbose_name=_('system'), choices=RoleplaySystems.choices)
    game_master = models.ForeignKey(
        to=constants.USER_MODEL, verbose_name=_('game master'), on_delete=models.CASCADE,
        related_name='gm_session_set', related_query_name='gm_session', db_index=True
    )
    world = models.ForeignKey(
        to=constants.PLACE_MODEL, verbose_name=_('world'), on_delete=models.CASCADE,
        related_name='session_set', related_query_name='session', db_index=True,
        limit_choices_to={'site_type': SiteTypes.WORLD}, blank=False, null=False,
    )

    class Meta:
        verbose_name = _('session')
        verbose_name_plural = _('sessions')
        ordering = ['-entry_created_at', 'name']

    def get_absolute_url(self):
        return reverse('roleplay:session:detail', kwargs={'pk': self.pk})

    def clean(self):
        # Don't allow non Worlds to be world
        try:
            if self.world.site_type != SiteTypes.WORLD:
                msg = _('world must be a world')
                raise ValidationError({'world': f'{msg}.'})
        except ValidationError as e:
            raise e
        except Session.world.RelatedObjectDoesNotExist:
            msg = _('world is required')
            raise ValidationError({'world': f'{msg}.'})

    def save(self, *args, **kwargs):
        Chat = apps.get_model(constants.CHAT_MODEL)
        self.full_clean()

        try:
            self.chat
        except Session.chat.RelatedObjectDoesNotExist:
            formatted_date = timezone.now().strftime('%Y%m%d_%H%M%S')
            chat_name = f'{self.name}_{formatted_date}'
            self.chat = Chat.objects.create(
                name=chat_name[:Chat.name.field.max_length]
            )
        finally:
            super().save(*args, **kwargs)
            # We add GM
            self.chat.users.add(self.game_master)
            # We add all players
            self.chat.users.add(*self.players.all())

    def __str__(self):
        created_at = self.entry_created_at.strftime('%Y-%m-%d')
        return f'{self.name} ({created_at})'
