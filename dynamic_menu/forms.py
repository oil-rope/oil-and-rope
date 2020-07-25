from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Div, Layout, Row
from django.utils.translation import gettext_lazy as _
from modeltranslation.forms import TranslationModelForm
from mptt.forms import TreeNodeChoiceField

from . import models


class DynamicMenuForm(TranslationModelForm):
    """
    This forms allows the user to create Menus in a easy way.
    """

    parent = TreeNodeChoiceField(
        label=_('Parent menu'),
        queryset=models.DynamicMenu.objects.all(),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'createMenuForm'
        self.display_name_container_id = 'menuDisplayNameContainer'
        self.helper.layout = Layout(
            Row(
                Column('prepended_text'),
                Column('name'),
                Column('appended_text'),
                Div(css_id=self.display_name_container_id),
                css_class='justify-content-around'
            ),
            Row(
                Column('url_resolver'),
                Column('extra_urls_args'),
                css_class='justify-content-around'
            )
        )

    class Meta:
        model = models.DynamicMenu
        fields = '__all__'
