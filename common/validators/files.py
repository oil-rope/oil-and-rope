import mimetypes

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from common.files.utils import max_size_file_mb


def validate_file_size(value):
    """
    Checks if file size is not large than FILE_UPLOAD_MAX_MEMORY_SIZE in Settings.
    """

    max_size = settings.FILE_UPLOAD_MAX_MEMORY_SIZE
    if value.size > max_size:
        mb_size = max_size_file_mb()
        max_size_msg = _('Size should not exceed %(megabytes)s MiB') % {'megabytes': mb_size}
        msg = _('File too large')
        raise ValidationError(f'{msg}. {max_size_msg}.')


def validate_music_file(value):
    """
    Check if file is a music type.
    """

    extensions = [key for key, value in mimetypes.types_map.items() if 'audio/' in value]
    if not value.name.endswith(tuple(extensions)):
        msg = _('File is not an audio')
        raise ValidationError(f'{msg}.')
