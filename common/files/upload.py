from django.utils import timezone


def default_upload_to(instance, file):
    """
    Uploads images to /app/model/date(Y/m/d/)/id/filename.
    It's generic for every model
    """

    date = timezone.now()
    formatted_date = date.strftime('%Y/%m/%d')
    app = instance._meta.app_label
    model = instance._meta.model_name
    identifier = instance.pk

    if not identifier:
        if hasattr(instance, 'tree_id'):
            identifier = instance.tree_id
        # TODO: Correct test cases
        else:  # pragma: no cover
            identifier = 'unknown_identifier'

    return '{}/{}/{}/{}/{}'.format(app, model, formatted_date, identifier, file)
