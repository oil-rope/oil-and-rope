import pathlib

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
