from django import forms


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


class TimeWidget(forms.TimeInput):
    """
    A widget using HTML5 time type.
    """

    input_type = 'time'
