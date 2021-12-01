import ast
import inspect

from django.apps import apps
from django.core.checks import Tags, Warning, register
from django.core.exceptions import FieldDoesNotExist


def get_argument(node, arg):
    """
    Checks for an argument in node and returns it, otherwise returns None.
    """

    for kw in node.value.keywords:
        if kw.arg == arg:
            return kw
    return None


def is_gettext_node(node):
    if not isinstance(node, ast.Call):
        return False

    # We assume gettext is aliased '_'.
    if not node.func.id == '_':  # type: ignore
        return False

    return True


def check_model(model):  # noqa
    """
    Checks a model to accomplish the following hints:

    - MC001: Model has `verbose_name`.
    - MC002: `verbose_name` uses gettext.
    - MC003: `verbose_name` is lowercase.
    - MC004: `help_text` uses gettext.
    - MC005: ForeignKey uses `db_index`.
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
            # GenericForeignKeys do not have verbose_name
            if field.__class__.__name__ == 'GenericForeignKey':
                continue
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
        else:
            if not is_gettext_node(verbose_name.value):
                yield Warning(
                    'Verbose name should use gettext',
                    hint='Use gettext on the verbose name.',
                    obj=field,
                    id='MC002',
                )
            else:
                value = verbose_name.value.args[0].s  # type: ignore
                if not all(w.islower() or w.isdigit() for w in value.split(' ')):
                    yield Warning(
                        'Words in verbose name must be all lower case',
                        hint='Change verbose name to "{}".'.format(value.lower()),
                        obj=field,
                        id='MC003',
                    )

        help_text = get_argument(node, 'help_text')
        if help_text is not None:
            if not is_gettext_node(help_text.value):
                yield Warning(
                    'Help text should use gettext',
                    hint='Use gettext on the help text.',
                    obj=field,
                    id='MC004',
                )

        if field.many_to_one:
            db_index = get_argument(node, 'db_index')
            if db_index is None:
                yield Warning(
                    'Must set db_index explicitly on a ForeignKey field',
                    hint='Set db_index on the field.',
                    obj=field,
                    id='MC005',
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
