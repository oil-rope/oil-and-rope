from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Div, Layout, Row
from django import forms
from django.utils.translation import gettext_lazy as _
from modeltranslation.forms import TranslationModelForm
from mptt.forms import TreeNodeChoiceField

from common.enums import AvailableIcons

from . import models


class DynamicMenuForm(TranslationModelForm):
    """
    This forms allows the user to create Menus in a easy way.
    """

    parent = TreeNodeChoiceField(
        label=_('Parent menu'),
        queryset=models.DynamicMenu.objects.all(),
    )

    prepended_text = forms.ChoiceField(
        label=_('Prepended icon'),
        choices=AvailableIcons.choices_with_empty,
        required=False
    )

    appended_text = forms.ChoiceField(
        label=_('Appended icon'),
        choices=AvailableIcons.choices_with_empty,
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'createMenuForm'
        self.display_name_container_id = 'menuDisplayNameContainer'
        self.display_url_resolver_id = 'menuDisplayURLResolver'
        self.helper.layout = Layout(
            Row(
                Column('prepended_text', css_class='col-md-3'),
                Column('name', css_class='col-md-3'),
                Column('appended_text', css_class='col-md-3'),
                Div(
                    css_id=self.display_name_container_id,
                    css_class='col-md-3 d-flex flex-column justify-content-center',
                    style='min-height: 50px'
                ),
                css_class='justify-content-around'
            ),
            Row(
                Column('url_resolver', css_class='col-md-4'),
                Column('extra_urls_args', css_class='col-md-4'),
                Div(
                    css_id=self.display_url_resolver_id,
                    css_class='col-md-4 d-flex flex-column justify-content-center',
                    style='min-height: 50px'
                ),
                css_class='justify-content-around'
            ),
            Row(
                Column('parent', css_class='col-md-6'),
                Column('menu_type', css_class='col-md-6'),
                css_class='justify-content-around'
            ),
        )

    class Meta:
        model = models.DynamicMenu
        fields = '__all__'
