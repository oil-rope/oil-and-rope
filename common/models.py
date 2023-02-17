import pathlib
import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import TracingMixin

from .constants import models as constants
from .files.upload import default_upload_to
from .validators.files import validate_file_size, validate_music_file


class Track(TracingMixin):
    """
    This models manages tracks either music, SFX, sounds...

    Attributes
    ----------
    id: :class:`int`
        Identifier.
    name: :class:`str`
        Name of the track.
    description: Optional[:class:`str`]
        Description about the track.
    owner: Optional[:class:`registration.User`]
        User that added this track.
    public: :class:`bool`
        `True` for track to be public.
    file: :class:`django.core.files.File`
        The file with the track.
    """

    id = models.BigAutoField(verbose_name=_('identifier'), primary_key=True, db_index=True)
    name = models.CharField(verbose_name=_('name'), max_length=50)
    description = models.TextField(verbose_name=_('description'), blank=True, null=False)
    owner = models.ForeignKey(
        verbose_name=_('owner'), to=constants.REGISTRATION_USER, to_field='id', on_delete=models.CASCADE,
        related_name='owner', db_index=True, null=True, blank=True,
    )
    public = models.BooleanField(verbose_name=_('public'), default=True)
    file = models.FileField(
        verbose_name=_('file'), upload_to=default_upload_to, validators=[validate_file_size, validate_music_file],
        max_length=254,
    )

    def __str__(self) -> str:
        file = pathlib.Path(self.file.name)  # We convert to pathlib.Path in order to get just name
        return f'{self.name} ({file.name})'


class Image(TracingMixin):
    """
    This model handles images associated to various models such a places, races, campaigns, sessions...
    Is created in order to tackle multiple image support.

    Parameters
    ----------
    id: :class:`~uuid.UUID`
        The unique identifier for the image.
    image: :class:`~django.db.models.fields.files.ImageField`
        The actual image uploaded.
    owner: :class:`~registration.models.User`
        The user that uploaded the image.
    content_type: :class:`~django.contrib.contenttypes.models.ContentType`
        Relation to the model this image is associated to.
    object_id: :class:`str`
        Identifier of the instance this image is associated to.
    content_object: :class:`~django.contrib.contenttypes.fields.GenericForeignKey`
        The actual object this image is associated to.
    """

    id = models.UUIDField(verbose_name=_('identifier'), primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(
        verbose_name=_('image'), upload_to=default_upload_to, validators=[validate_file_size], max_length=255,
    )
    owner = models.ForeignKey(
        verbose_name=_('owner'), to=constants.REGISTRATION_USER, db_index=True, to_field='id', related_name='image_set',
        on_delete=models.CASCADE, null=False, blank=False,
    )
    content_type = models.ForeignKey(
        verbose_name=_('model associated'), to=constants.CONTENT_TYPE, on_delete=models.CASCADE,
        related_name='image_set', db_index=True, null=False, blank=False,
    )
    object_id = models.CharField(
        verbose_name=_('object identifier'), db_index=True, null=False, blank=False, max_length=255,
    )
    content_object = GenericForeignKey(ct_field='content_type', fk_field='object_id')

    class Meta:
        verbose_name = _('image')
        verbose_name_plural = _('images')
        ordering = ['-entry_created_at', '-entry_updated_at']
        # Indexes are not automatically created for Generic Foreign keys
        # https://docs.djangoproject.com/en/4.1/ref/contrib/contenttypes/#django.contrib.contenttypes.fields.GenericForeignKey
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self) -> str:
        return f'{self.image.name} [{self.owner.username}] ({self.id})'


class Vote(TracingMixin):
    """
    This model will handle voting on either a :class:`~roleplay.model.Campaign`, :class:`~roleplay.models.Place` or
    any other needed model with voting

    Parameters
    ----------
    id: :class:`~uuid.UUID`
        The unique identifier of the vote.
        We use vote instead of :class:`int` since there'll be a lot of records of this.
    is_positive: :class:`bool`
        Declares if the vote was positive. In case a vote has not yet been made we don't need to declare it since
        it won't be a record in this model.
    user: :class:`~registration.models.User`
        The user that did the vote.
    content_type: :class:`~django.contrib.contenttypes.models.ContentType`
        The model associated to the voting.
    object_id: :class:`int`
        The identifier of the associated object.
        NOTE: This will work as long as the identifier is an int, we need to have that in mind.
    """

    VOTABLE_MODELS = ('campaign', 'place')
    VOTABLE_APP_LABELS = ('roleplay', )

    id = models.UUIDField(verbose_name=_('identifier'), primary_key=True, default=uuid.uuid4, editable=False)
    is_positive = models.BooleanField(verbose_name=_('positive vote?'), default=True)
    user = models.ForeignKey(
        verbose_name=_('user'), to=constants.REGISTRATION_USER, to_field='id', on_delete=models.CASCADE,
        related_name='user', db_index=True, null=False, blank=False,
    )
    content_type = models.ForeignKey(
        verbose_name=_('model associated'), to=constants.CONTENT_TYPE, on_delete=models.CASCADE,
        related_name='vote_set', db_index=True, null=False, blank=False,
        limit_choices_to={'model__in': VOTABLE_MODELS, 'app_label__in': VOTABLE_APP_LABELS},
    )
    object_id = models.PositiveBigIntegerField(
        verbose_name=_('object identifier'), db_index=True, null=False, blank=False
    )
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = _('vote')
        verbose_name_plural = _('votes')
        unique_together = ('user', 'content_type', 'object_id')
        indexes = [
            models.Index(fields=['user', 'content_type', 'object_id']),
        ]

    def __str__(self):
        msg = _('%(user)s voted %(is_positive)s on %(model)s (%(id)s)') % {
            'user': self.user.username,
            'is_positive': '+' if self.is_positive else '-',
            'model': f'{self.content_type.app_label}.{self.content_type.model}',
            'id': self.object_id,
        }
        return msg
