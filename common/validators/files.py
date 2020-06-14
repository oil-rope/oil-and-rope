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
        max_size_msg = _('Size should not exceed {} MiB').format(mb_size)
        raise ValidationError('{file_too_large}. {max_size}.'.format(
            file_too_large=_('File too large'),
            max_size=max_size_msg
        ))
