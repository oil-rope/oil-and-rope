from django.db import models
from django.utils import timezone

from common import models as common_models


def default_upload_to(instance: models.Model, filename: str) -> str:
    """
    Uploads images to /app/model/date(Y/m/d/)/id/filename.
    It's generic for every model
    """

    date = timezone.now()
    formatted_date = date.strftime('%Y/%m/%d')
    app = instance._meta.app_label
    model = instance._meta.model_name
    if isinstance(instance, common_models.Image):
        identifier = instance.owner.pk
    else:
        identifier = instance.pk

    if not identifier:
        if hasattr(instance, 'tree_id'):
            identifier = instance.tree_id
        # TODO: Correct test cases
        else:  # pragma: no cover
            identifier = 'unknown_identifier'

    return '{}/{}/{}/{}/{}'.format(app, model, formatted_date, identifier, filename)
