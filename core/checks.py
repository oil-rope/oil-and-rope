import ast
import inspect

from django.apps import apps
from django.core.checks import Tags, Warning, register
from django.db.models import FieldDoesNotExist


def get_argument(node, arg):
    """
    Checks for an argument in node and returns it, otherwise returns None.
    """

    for kw in node.value.keywords:
        if kw.arg == arg:
            return kw
    return None


def check_model(model):
    """
    Checks a model to accomplish the following hints:

    - MC001: Model has `verbose_name`.
    """

    model_source = inspect.getsource(model)
    model_node = ast.parse(model_source)

    for node in model_node.body[0].body:

        # Check for Top-Level
        if not isinstance(node, ast.Assign):  # pragma: no cover
            continue
        # Node must have targets
        if len(node.targets) != 1:
            continue
        # Looking for name target (name of the field)
        if not isinstance(node.targets[0], ast.Name):  # pragma: no cover
            continue

        field_name = node.targets[0].id
        try:
            # Node is a field
            field = model._meta.get_field(field_name)
        except FieldDoesNotExist:
            continue

        # Looking for verbose_name
        verbose_name = get_argument(node, 'verbose_name')
        if verbose_name is None:
            yield Warning(
                'Field has no verbose name.',
                hint='Set verbose name on field {}.'.format(field.name),
                obj=field,
                id='MC001',
            )


@register(Tags.models)
def check_models(app_configs, **kwargs):
    errors = []
    for app in apps.get_app_configs():
        # Skip third-party
        if app.path.find('site-packages') > -1:
            continue
        for model in app.get_models():
            for check_message in check_model(model):
                errors.append(check_message)

    return errors
