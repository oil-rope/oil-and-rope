from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Reset, Layout, Field, Row, Column
from django import forms
from django.utils.translation import gettext_lazy as _

from . import models


class WorldForm(forms.ModelForm):

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(
                Column(
                    Field('name'),
                    css_class='col-12'
                ),
                Column(
                    Field('description'),
                    css_class='col-12'
                ),
                Column(
                    Field('image'),
                    css_class='col-12'
                )
            ),
            Row(
                Submit('submit', _('Create'), css_class='btn btn-extra col-5'),
                Reset('reset', _('Clean'), css_class='btn btn-dark col-5'),
                css_class='justify-content-around'
            )
        )

    class Meta:
        exclude = ('user', 'parent_site', 'site_type')
        model = models.Place

    def save(self, commit=True):
        if self.user:
            self.instance.user = self.user
        self.instance.site_type = models.Place.WORLD
        return super().save(commit)
