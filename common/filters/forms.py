from crispy_forms.helper import FormHelper
from crispy_forms.layout import Reset, Submit
from django import forms
from django.utils.translation import gettext_lazy as _


class BasicFilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'GET'
        self.helper.form_class = 'row row-cols-lg-auto g-3 align-items-center justify-content-between'
        self.helper.add_input(Submit('submit', _('search').capitalize()))
        self.helper.add_input(Reset('reset', _('reset').capitalize(), css_class='btn btn-dark'))
