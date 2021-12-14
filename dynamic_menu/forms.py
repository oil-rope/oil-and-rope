from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Div, Fieldset, Layout, Reset, Row, Submit
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
        label=_('parent menu'),
        queryset=models.DynamicMenu.objects.all(),
        required=False
    )

    prepended_text = forms.ChoiceField(
        label=_('prepended icon'),
        choices=AvailableIcons.choices_with_empty,
        required=False
    )

    appended_text = forms.ChoiceField(
        label=_('appended icon'),
        choices=AvailableIcons.choices_with_empty,
        required=False
    )

    permissions_required = forms.CharField(
        help_text=_('permissions must be separated by \',\' (auth.view_user, roleplay.delete_world, ...)'),
        required=False
    )

    related_models = forms.CharField(
        help_text=_('models must be separated by \',\' (registration.User, roleplay.World, auth.Group, ...)'),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'createMenuForm'
        self.display_name_container_id = 'menuDisplayNameContainer'
        self.display_url_resolver_id = 'menuDisplayURLResolver'
        self.helper.layout = Layout(
            Fieldset(
                _('naming'),
                Row(
                    Column('prepended_text', css_class='col-md-4 col-lg-3'),
                    Column('name', css_class='col-md-4 col-lg-3'),
                    Column('appended_text', css_class='col-md-4 col-lg-3'),
                    Div(
                        css_id=self.display_name_container_id,
                        css_class='col-md-12 col-lg-3 d-flex flex-column justify-content-center',
                        style='min-height: 50px'
                    ),
                    css_class='justify-content-around'
                ),
                css_class='mb-3'
            ),
            Fieldset(
                _('direction'),
                Row(
                    Column('url_resolver', css_class='col-md-6 col-lg-4'),
                    Column('extra_urls_args', css_class='col-md-6 col-lg-4'),
                    Div(
                        css_id=self.display_url_resolver_id,
                        css_class='col-md-12 col-lg-4 d-flex flex-column justify-content-center',
                        style='min-height: 50px'
                    ),
                    css_class='justify-content-around'
                ),
                css_class='mb-3'
            ),
            Fieldset(
                _('permissions'),
                Row(
                    Column('permissions_required', css_class='col-md-6 col-lg-3'),
                    Column('related_models', css_class='col-md-6 col-lg-3'),
                    Column('staff_required', css_class='col-md-6 col-lg-3 align-self-lg-center'),
                    css_class='justify-content-around'
                ),
                css_class='mb-3'
            ),
            Row(
                Column('parent', css_class='col-md-4'),
                Column('menu_type', css_class='col-md-4'),
                Column('order', css_class='col-md-4'),
                css_class='justify-content-around'
            ),
            Row(
                Column('description', css_class='col-12'),
                css_class='justify-content-around'
            ),
            Row(
                Column(
                    Submit('submit', _('create'), css_class='w-100'),
                    css_class='col-6 col-lg-4'
                ),
                Column(
                    Reset('reset', _('clear'), css_class='w-100 btn-secondary'),
                    css_class='col-6 col-lg-4'
                ),
                css_class='justify-content-around'
            ),
        )

    def clean_permissions_required(self):
        """
        Transforms permissions :class:`str` into a parsed :class:`list`.
        """

        data = self.cleaned_data['permissions_required']

        if not data:
            return data

        data = data.replace(' ', '')
        data = data.split(',')
        return data

    def clean_related_models(self):
        """
        Transforms models :class:`str` into a parsed :class:`list`.
        """

        data = self.cleaned_data['related_models']

        if not data:
            return data

        data = data.replace(' ', '')
        data = data.split(',')
        return data

    def save(self, commit=True):
        super().save(commit=False)

        if commit:
            self.instance.save()
            perms = self.cleaned_data['permissions_required']
            self.instance.add_permissions(*perms)

        return self.instance

    class Meta:
        model = models.DynamicMenu
        fields = (
            'prepended_text', 'name', 'appended_text', 'description', 'url_resolver', 'extra_urls_args',
            'parent', 'menu_type', 'order', 'permissions_required', 'staff_required',
        )
