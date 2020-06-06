from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Field, Layout, Reset, Row, Submit
from django import forms
from django.utils.translation import gettext_lazy as _

from . import models


class WorldForm(forms.ModelForm):

    def __init__(self, owner, user=None, submit_text=_('Create'), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.owner = owner
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(
                Column(
                    Field('name', placeholder='Middle-Earth, Narnia, Argos...'),
                    css_class='col-12 col-lg-7'
                ),
                Column(
                    Field('description',
                          placeholder=_('Write something about your world, its civilizations, its culture...')),
                    css_class='col-12 col-lg-7'
                ),
                Column(
                    Field('image'),
                    css_class='col-12 col-lg-7'
                ),
                css_class='justify-content-lg-around'
            ),
            Row(
                Submit('submit', submit_text, css_class='btn btn-primary col-5 col-lg-6'),
                Reset('reset', _('Clean'), css_class='btn btn-secondary col-5 d-lg-none'),
                css_class='justify-content-around'
            )
        )

    class Meta:
        exclude = ('user', 'parent_site', 'site_type', 'owner')
        model = models.Place
        help_texts = {
            'image': _('A picture is worth a thousand words') + '.'
        }

    def save(self, commit=True):
        if self.user:
            self.instance.user = self.user
        self.instance.owner = self.owner
        self.instance.site_type = models.Place.WORLD
        return super().save(commit)
