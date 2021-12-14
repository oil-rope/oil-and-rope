from crispy_forms.helper import FormHelper
from django import forms
from django.utils.translation import gettext_lazy as _
from modeltranslation.forms import TranslationModelForm
from mptt.forms import TreeNodeChoiceField

from common.enums import AvailableIcons

from .. import models
from .layout import DynamicMenuLayout


class DynamicMenuForm(TranslationModelForm):
    """
    This forms allows the user to create Menus in a easy way.
    """

    parent = TreeNodeChoiceField(
        label=_('parent menu').title(),
        queryset=models.DynamicMenu.objects.all(),
        required=False
    )

    prepended_text = forms.ChoiceField(
        label=_('prepended icon').title(),
        choices=AvailableIcons.choices_with_empty,
        required=False
    )

    appended_text = forms.ChoiceField(
        label=_('appended icon').title(),
        choices=AvailableIcons.choices_with_empty,
        required=False
    )

    permissions_required = forms.CharField(
        help_text=_(
            'permissions must be separated by \',\' (auth.view_user, roleplay.delete_world, ...)'
        ).capitalize(),
        required=False
    )

    related_models = forms.CharField(
        help_text=_(
            'models must be separated by \',\' (registration.User, roleplay.World, auth.Group, ...)'
        ).capitalize(),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.form_id = 'createMenuForm'
        self.helper.layout = DynamicMenuLayout()

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
