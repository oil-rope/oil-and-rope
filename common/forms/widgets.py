from django import forms
from django.db import models


class NameDisplayModelChoiceField(forms.ModelChoiceField):
    """
    Based on :class:`forms.ModelChoiceField` we change the :method:`forms.ModelChoiceField.label_from_instance` to use
    the instance column `name`.
    """

    def label_from_instance(self, obj: models.Model) -> str:
        return f'{obj.name}'


class DateTimeWidget(forms.DateInput):
    """
    Widget using HTML5 with type 'datetime-local'
    """

    input_type = 'datetime-local'

    def __init__(self, *args, **kwargs):
        kwargs['format'] = '%Y-%m-%dT%H:%M'
        super().__init__(*args, **kwargs)


class DateWidget(forms.DateInput):
    """
    A widget using HTML5 date type.
    """

    input_type = 'date'

    def __init__(self, *args, **kwargs):
        kwargs['format'] = '%Y-%m-%d'
        super().__init__(*args, **kwargs)
