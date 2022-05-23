from crispy_forms.helper import FormHelper
from django import forms
from django.apps import apps

from common.constants import models

from .layouts import CampaignFilterLayout

Campaign = apps.get_model(models.ROLEPLAY_CAMPAIGN)


class CampaignFilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'GET'
        self.helper.form_class = 'row row-cols-lg-auto g-3 align-items-center justify-content-center'
        self.helper.layout = CampaignFilterLayout()
