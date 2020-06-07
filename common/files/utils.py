from django.conf import settings


def max_size_file_mb():
    mb_size = settings.FILE_UPLOAD_MAX_MEMORY_SIZE / 1024 / 1024
    mb_size = int(mb_size) if mb_size.is_integer() else mb_size
    return mb_size
