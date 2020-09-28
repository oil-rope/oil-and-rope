from django import forms


class DateWidget(forms.DateInput):
    """
    A widget using HTML5 date type.
    """

    def __init__(self, attrs=None, format=None):
        if not attrs:
            attrs = {'type': 'date'}
        super().__init__(attrs=attrs, format=format)


class TimeWidget(forms.TimeInput):
    """
    A widget using HTML5 time type.
    """

    def __init__(self, attrs=None, format=None):
        if not attrs:
            attrs = {'type': 'time'}
        super().__init__(attrs=attrs, format=format)
