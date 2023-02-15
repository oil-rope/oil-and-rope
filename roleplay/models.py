import uuid
from typing import TYPE_CHECKING, Optional, Type

from ckeditor.fields import RichTextField
from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import m2m_changed
from django.shortcuts import resolve_url
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

from bot.models import Channel
from common.constants import models as constants
from common.files.upload import default_upload_to
from common.validators import validate_file_size
from core.models import TracingMixin
from roleplay.enums import RoleplaySystems

from . import managers
from .enums import ICON_RESOLVERS, DomainTypes, SiteTypes

if TYPE_CHECKING:
    from chat.models import Chat


class TraitType(TracingMixin):
    """
    List of types of traits.

    id: :class:`int`
        Unique identifier of the trait.
    name: :class:`str`
        The name of the type.
    description: :class:`str`
        Description of the trait type.
    system: :class:`int`
        Roleplay system associated.
    """

    id = models.BigAutoField(verbose_name=_('identifier'), primary_key=True)
    name = models.CharField(verbose_name=_('name'), max_length=50, null=False, blank=False)
    description = models.TextField(verbose_name=_('description'), null=False, blank=True)
    system = models.SmallIntegerField(
        verbose_name=_('system'), choices=RoleplaySystems.choices, null=False, blank=False, db_index=True,
    )

    class Meta:
        verbose_name = _('type of trait')
        verbose_name_plural = _('types of trait')
        ordering = ['-entry_created_at', 'name', '-entry_updated_at']
        unique_together = [
            ('name', 'system'),
        ]

    def __str__(self):
        return f'{self.name} [{self.id}]'


class Trait(TracingMixin):
    """
    Declares generic traits that can be used for any roleplay model.

    Parameters
    ----------
    id: `uuid.UUID`
        Unique identifier of the instance.
    name: :class:`str`
        The name of the trait.
    description: :class:`str`
        The description of the trait.
    type: :class:`~roleplay.models.TraitType`
        The type of trait.
    source: :class:`str`
        The source this information comes from.
    creator: :class:`~typing.Optional[registration.models.User]`
        The user that created the trait.
    content_type: :class:`~django.contrib.contenttypes.models.ContentType`
        The model this instance is related to.
    object_id: :class:`str`
        The unique identifier for an instance in the given model on `content_type`.
    content_object: :class:`~django.contrib.contenttypes.fields.GenericForeignKey`
        The actual instance related.
    """

    id = models.UUIDField(verbose_name=_('identifier'), primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(verbose_name=_('name'), null=False, blank=False, max_length=255)
    description = models.TextField(verbose_name=_('description'), null=False, blank=True)
    type = models.ForeignKey(
        verbose_name=_('type'), to=constants.ROLEPLAY_TRAIT_TYPE, to_field='id', on_delete=models.CASCADE,
        related_name='race_set', db_index=True,
    )
    source = models.CharField(
        verbose_name=_('source'), max_length=255, null=False, blank=True,
        help_text=_('where does this information come from?'),
    )
    source_link = models.URLField(
        verbose_name=_('source link'), null=False, blank=True, help_text=_('link to the source information'),
    )
    creator = models.ForeignKey(
        verbose_name=_('creator'), to=constants.REGISTRATION_USER, to_field='id', on_delete=models.CASCADE,
        related_name='trait_set', db_index=True,
    )
    content_type = models.ForeignKey(
        verbose_name=_('model associated'), to=constants.CONTENT_TYPE, on_delete=models.CASCADE,
        related_name='trait_set', to_field='id', db_index=True,
    )
    object_id = models.CharField(
        verbose_name=_('object identifier'), db_index=True, null=False, blank=False, max_length=255,
    )
    content_object = GenericForeignKey(ct_field='content_type', fk_field='object_id')

    class Meta:
        verbose_name = _('trait')
        verbose_name_plural = _('traits')
        ordering = ['-entry_created_at', 'name', '-entry_updated_at']

    def __str__(self):
        return f'{self.name} ({self.type.get_system_display()}) [{self.id}]'


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
    description = models.TextField(verbose_name=_('description'), null=False, blank=True)
    domain_type = models.PositiveSmallIntegerField(
        verbose_name=_('domain type'), choices=DomainTypes.choices, default=DomainTypes.DOMAIN, null=False, blank=False
    )
    image = models.ImageField(verbose_name=_('image'), upload_to=default_upload_to, null=False, blank=True)

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
        domain_type = DomainTypes(self.domain_type)
        return f'{self.name} [{domain_type.label.title()}]'


# TODO: MPTTModel is unmaintained, we need to change it
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
    owner: :class:`registration.User`
        The person who created this map.
    is_public: :class:`bool`
        Declares if Place is public.
    """

    ICON_RESOLVERS = ICON_RESOLVERS

    objects = managers.PlaceManager()

    name = models.CharField(verbose_name=_('name'), max_length=100, null=False, blank=False)
    description = RichTextField(verbose_name=_('description'), null=False, blank=True)
    site_type = models.PositiveSmallIntegerField(
        verbose_name=_('site type'), choices=SiteTypes.choices, default=SiteTypes.TOWN, null=False, blank=False
    )
    image = models.ImageField(
        verbose_name=_('image'), upload_to=default_upload_to, null=False, blank=True, validators=[validate_file_size]
    )
    parent_site = TreeForeignKey(
        to='self', verbose_name=_('parent site'), on_delete=models.CASCADE, null=True, blank=True,
        related_name='children_sites', db_index=True
    )
    owner = models.ForeignKey(
        to=constants.REGISTRATION_USER, on_delete=models.CASCADE, related_name='place_set', verbose_name=_('owner'),
        db_index=True,
    )
    is_public = models.BooleanField(verbose_name=_('public'), default=False)

    @cached_property
    def images(self):
        images = []
        if self.image:
            images.extend([self.image])
        images.extend([obj.image for obj in self.get_descendants().filter(image__isnull=False) if obj.image])
        return images

    def resolve_icon(self):
        return '<i class="{}"></i>'.format(self.ICON_RESOLVERS.get(self.site_type, ''))

    def get_absolute_url(self):
        return resolve_url('roleplay:place:detail', pk=self.pk)

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

    def __str__(self):
        return self.name


class Race(TracingMixin):
    """
    Model to manage Races.

    Parameters
    ----------
    id: :class:`int`
        The identifier of the race.
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
        Modifier for charisma.
    affected_by_armor: :class:`boolean`
        Declares if this race is affected by any penalty that armor can give.
    traits: :class:`list[roleplay.models.Trait`]
        List of traits associated to this race.
    images: :class:`list[django.core.files.uploadedfile.UploadedFile]`
        Image for the race.
    owner: :class:`~registration.models.User`
        User that created.
    place: :class:`~typing.Optional[roleplay.models.Place]`
        Place where this race can be found.
    campaign: :class:`~typing.Optional[roleplay.models.Campaign]`
        Campaign where this race is played.
    """

    id = models.BigAutoField(verbose_name=_('identifier'), primary_key=True)
    name = models.CharField(verbose_name=_('name'), max_length=50, null=False, blank=False)
    description = models.TextField(verbose_name=_('description'), null=False, blank=True)
    strength = models.SmallIntegerField(verbose_name=_('strength'), default=0, null=False, blank=True)
    dexterity = models.SmallIntegerField(verbose_name=_('dexterity'), default=0, null=False, blank=True)
    constitution = models.SmallIntegerField(verbose_name=_('constitution'), default=0, null=False, blank=True)
    intelligence = models.SmallIntegerField(verbose_name=_('intelligence'), default=0, null=False, blank=True)
    wisdom = models.SmallIntegerField(verbose_name=_('wisdom'), default=0, null=False, blank=True)
    charisma = models.SmallIntegerField(verbose_name=_('charisma'), default=0, null=False, blank=True)
    affected_by_armor = models.BooleanField(
        verbose_name=_('affected by armor'), default=True,
        help_text=_('declares if this race is affected by armor penalties'), null=False, blank=True,
    )
    traits = GenericRelation(
        verbose_name=_('traits'), to=constants.ROLEPLAY_TRAIT, related_name='race_set',
        content_type_field='content_type', object_id_field='object_id',
    )
    images = GenericRelation(
        verbose_name=_('images'), to=constants.COMMON_IMAGE, related_name='race_set', content_type_field='content_type',
        object_id_field='object_id',
    )
    owner = models.ForeignKey(
        verbose_name=_('owner'), to=constants.REGISTRATION_USER, to_field='id', related_name='race_set', db_index=True,
        null=False, blank=False, on_delete=models.CASCADE,
    )
    campaign = models.ForeignKey(
        verbose_name=_('campaign'), to=constants.ROLEPLAY_CAMPAIGN, to_field='id', related_name='race_set',
        db_index=True, null=True, blank=False, on_delete=models.CASCADE,
    )
    place = models.ForeignKey(
        verbose_name=_('place'), to=constants.ROLEPLAY_PLACE, to_field='id', related_name='race_set', db_index=True,
        null=True, blank=False, on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _('race')
        verbose_name_plural = _('races')
        ordering = ['-entry_created_at', 'name']

    def clean(self):
        if not self.campaign and not self.place:
            raise ValidationError(_('either a campaign or a place should be indicated.').capitalize())

    def get_absolute_url(self):
        return resolve_url('roleplay:race:detail', pk=self.pk)

    @property
    def abilities_display(self) -> Optional[str]:
        """
        We iter between the ability modifiers in order to return a human-friendly format to quickly see which abilities
        modifies the race.
        """

        static_list_of_abilities = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
        ability_modifiers = [ability for ability in static_list_of_abilities if getattr(self, ability) != 0]

        if ability_modifiers:
            abilities_display: list[str] = []
            for ability in ability_modifiers:
                ability_value = getattr(self, ability)
                ability_name = self._meta.get_field(ability).verbose_name.capitalize()
                # NOTE: We assume no ability will be more than 3 characters
                ability_display = f'{getattr(self, ability)} {ability_name:.3}.'
                if ability_value > 0:
                    # We add a '+' to the display just for UX/UI
                    ability_display = f'+{ability_display}'
                abilities_display.append(ability_display)
            return ', '.join(abilities_display)
        return None

    def __str__(self):
        return f'{self.name} [{self.pk}]'


# TODO: When Character Model is set we should add PCs and NPCs as part of campaign
class Campaign(TracingMixin):
    """
    This model manages campaign for roleplay sessions.
    A campaign is a set-up for a game. This will have sessions related which will be the sessions themselves.
    A campaign can be public in order for everyone to see it or private in order to be only visible to the persons
    in users.

    Parameters
    ----------
    id: :class:`int`
        Identifier of the object.
    name: :class:`str`
        Name of the campaign.
    description: Optional[:class:`str`]
        Description of the campaign.
    gm_info: Optional[:class:`str`]
        Information specific to the game master.
    summary: Optional[:class:`str`]
        A one line description of the campaign.
    system: :class:`int`
        System used.
    cover_image: Optional[:class:`str`]
        Path to the cover image of the campaign.
    owner: :class:`~registration.models.User`
        Owner of the campaign.
        This is used in order to have track of the person who created the campaign.
        This user can and can be not a player of the campaign.
    is_public: Optional[:class:`bool`]
        Declares if the campaign is public or not.
    users: List[:class:`~registration.models.User`]
        List of players that are part of the campaign.
    place: :class:`~roleplay.models.Place`
        World where the campaign is happening.
    start_date: Optional[:class:`datetime.date`]
        Date when the campaign starts.
    end_date: Optional[:class:`datetime.date`]
        Date when the campaign ends.
    discord_channel_id: Optional[:class:`str`]
        The discord channel ID where the campaign is happening.
        This will be used to send messages to the discord channel.
    chat: :class:`~chat.models.Chat`
        Chat used by the campaign.
    """

    objects = managers.CampaignManager()

    id = models.BigAutoField(verbose_name=_('identifier'), primary_key=True, db_index=True, null=False, blank=False)
    name = models.CharField(verbose_name=_('name'), max_length=50)
    description = models.TextField(verbose_name=_('description'), null=False, blank=True)
    gm_info = models.TextField(
        verbose_name=_('game master information'), help_text=_('information specific to the game master.'),
        null=False, blank=True,
    )
    summary = models.CharField(verbose_name=_('summary'), max_length=254, null=False, blank=True)
    system = models.PositiveSmallIntegerField(verbose_name=_('system'), choices=RoleplaySystems.choices)
    cover_image = models.ImageField(
        verbose_name=_('cover image'), upload_to=default_upload_to, validators=[validate_file_size], null=False,
        blank=True,
    )
    owner = models.ForeignKey(
        verbose_name=_('owner'), to=constants.REGISTRATION_USER, related_name='campaign_owned_set',
        on_delete=models.CASCADE, db_index=True,
    )
    is_public = models.BooleanField(
        verbose_name=_('public'), help_text=_('can this campaign be accessed by anyone?'), default=False,
    )
    users = models.ManyToManyField(
        to=constants.REGISTRATION_USER, verbose_name=_('players'), related_name='campaign_set',
        through=constants.ROLEPLAY_PLAYER_IN_CAMPAIGN, through_fields=('campaign', 'user'),
    )
    place = models.ForeignKey(
        verbose_name=_('world'), to=constants.ROLEPLAY_PLACE, related_name='campaign_set', on_delete=models.CASCADE,
        db_index=True, null=False, blank=False, limit_choices_to={'site_type': SiteTypes.WORLD},
    )
    start_date = models.DateField(verbose_name=_('start date'), null=True, blank=True)
    end_date = models.DateField(verbose_name=_('end date'), null=True, blank=True)
    discord_channel_id = models.CharField(
        verbose_name=_('identifier for discord channel'), max_length=254, null=False, blank=True,
    )
    chat = models.OneToOneField(
        to=constants.CHAT, verbose_name=_('chat'), on_delete=models.CASCADE,
        related_name='campaign_set', db_index=True, blank=False, null=False,
    )
    votes = GenericRelation(
        verbose_name=_('votes'), to=constants.COMMON_VOTE, related_query_name='campaign_set',
        content_type_field='content_type', object_id_field='object_id',
    )

    def get_game_masters(self):
        """
        Returns the list of game masters.
        """

        gms = self.users.filter(player_in_campaign_set__is_game_master=True)
        return list(gms)
    game_masters = cached_property(get_game_masters)

    @property
    def discord_channel(self) -> Optional[Channel]:
        if self.discord_channel_id:
            return Channel(id=self.discord_channel_id)
        return None

    class Meta:
        verbose_name = _('campaign')
        verbose_name_plural = _('campaigns')
        ordering = ['-entry_created_at', 'name']

    def vote(self, user, vote):
        """
        Votes for the campaign.

        Parameters
        ----------
        user: :class:`~registration.models.User`
            User that is voting.
        vote: :class:`bool`
            Declares if vote is positive or negative.
        """

        return self.votes.create(user=user, is_positive=vote)

    def add_game_masters(self, *users):
        """
        Adds given users as game masters.
        """

        PlayerInCampaign: Type['PlayerInCampaign'] = apps.get_model(constants.ROLEPLAY_PLAYER_IN_CAMPAIGN)
        entries_to_create = [PlayerInCampaign(user=user, campaign=self, is_game_master=True) for user in users]
        objs = PlayerInCampaign.objects.bulk_create(entries_to_create)
        return objs

    def get_absolute_url(self):
        return resolve_url('roleplay:campaign:detail', pk=self.pk)

    def clean(self):
        """
        Validates the campaign.
        """

        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError(_('start date must be before end date.').capitalize())

    def __str__(self):
        return f'{self.name} [{self.pk}]'


def sync_campaign_related_users_to_chat(
    sender: Type['PlayerInCampaign'],
    instance: Campaign,
    action: str,
    pk_set: set[str],
    **kwargs
):
    """
    This signal will synchronize players of campaign with users in chat, so they are added or remove from campaign's
    chat.
    """

    chat: 'Chat' = instance.chat

    if action in ('post_add', ):
        chat.users.add(*pk_set)
    if action in ('post_remove', ):
        chat.users.remove(*pk_set)


m2m_changed.connect(sync_campaign_related_users_to_chat, sender=Campaign.users.through)


class PlayerInCampaign(TracingMixin):
    """
    This models manages the 'M2M through' for :class:`~roleplay.models.Campaign`.

    Parameters
    ---------
    id: :class:`int`
        The identifier of the object.
    campaign: :class:`~roleplay.models.Campaign`
        The related campaign.
    user: :class:`~registration.models.User`
        The related user.
    """

    id = models.BigAutoField(verbose_name=_('identifier'), primary_key=True, null=False, blank=False, db_index=True)
    user = models.ForeignKey(
        verbose_name=_('user'), to=constants.REGISTRATION_USER, on_delete=models.CASCADE, to_field='id',
        related_name='player_in_campaign_set', db_index=True, null=False, blank=False,
    )
    campaign = models.ForeignKey(
        verbose_name=_('campaign'), to=constants.ROLEPLAY_CAMPAIGN, on_delete=models.CASCADE, to_field='id',
        related_name='player_in_campaign_set', db_index=True, null=False, blank=False,
    )
    is_game_master = models.BooleanField(verbose_name=_('game master'), default=False)

    class Meta:
        verbose_name = _('player in campaign')
        verbose_name_plural = _('players in campaign')
        ordering = ['-entry_created_at', 'user__username']
        unique_together = [
            ('user', 'campaign'),
        ]

    def __str__(self):
        str_model = _('%(player)s in campaign %(campaign)s (Game Master: %(is_game_master)s)') % {
            'player': self.user.username, 'campaign': self.campaign.name, 'is_game_master': self.is_game_master,
        }
        return str_model


class Session(TracingMixin):
    """
    This model manages sessions playing by the users.

    Parameters
    ----------
    campaign: :class:`~roleplay.models.Campaign`
        The related campaign.
    name: `str`
        Name of the session.
    description: Optional[`str`]
        Description of the session.
    plot: `str`
        Plot of the session.
    gm_info: Optional[`str`]
        Information specific to the game master.
    next_game: Optional[datetime.datetime]
        Next session's date.
    image: Optional[`str`]
        Cover image for this session.
    """

    objects = managers.SessionManager()

    id = models.AutoField(verbose_name=_('identifier'), primary_key=True, blank=False, null=False, db_index=True)
    campaign = models.ForeignKey(
        verbose_name=_('campaign'), to=constants.ROLEPLAY_CAMPAIGN, on_delete=models.CASCADE, to_field='id',
        related_name='session_set', db_index=True, null=False, blank=False,
    )
    name = models.CharField(verbose_name=_('title'), max_length=100, null=False, blank=False)
    description = models.TextField(verbose_name=_('description'), null=False, blank=True)
    plot = models.CharField(
        verbose_name=_('plot'), max_length=254, help_text=_('one line summary.'), null=False, blank=True,
    )
    gm_info = models.TextField(
        verbose_name=_('game master info'), help_text=_('information specific to the game master.'),
        null=False, blank=True,
    )
    next_game = models.DateTimeField(
        verbose_name=_('next session'), auto_now=False, auto_now_add=False, null=True, blank=True,
    )
    image = models.ImageField(
        verbose_name=_('cover'), upload_to=default_upload_to, validators=[validate_file_size], null=False, blank=True,
    )

    class Meta:
        verbose_name = _('session')
        verbose_name_plural = _('sessions')
        ordering = ['-next_game', 'name', '-entry_updated_at']

    def get_absolute_url(self):
        return resolve_url('roleplay:session:detail', pk=self.pk)

    def __str__(self):
        return f'{self.name} [{self.campaign.get_system_display()}]'
