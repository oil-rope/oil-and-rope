from crispy_forms.helper import FormHelper
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

    class Meta:
        model = models.DynamicMenu
        fields = '__all__'
