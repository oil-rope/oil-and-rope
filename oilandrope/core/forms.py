from django import forms

class DateHTML5Field(forms.DateField):
    """
    Field that renders `type="date"`.
    """

    def __init__(self, *args, **kwargs):
        super(DateHTML5Field, self).__init__(*args, **kwargs)
        self.widget = forms.DateInput(attrs={'type': 'date'})
