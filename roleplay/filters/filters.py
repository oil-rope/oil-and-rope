import django_filters as filters
from django.apps import apps
from django.db.models import Q
from django.forms.widgets import CheckboxInput
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from common.constants import models

from .forms import CampaignFilterForm

Campaign = apps.get_model(models.ROLEPLAY_CAMPAIGN)


class CampaignFilter(filters.FilterSet):
    place = filters.CharFilter(field_name='place__name', lookup_expr='contains')
    owner = filters.CharFilter(field_name='owner__username', lookup_expr='contains')
    active = filters.BooleanFilter(
        field_name='end_date', method='get_active', label=_('active'),
        help_text=_('search only for active campaigns'), widget=CheckboxInput,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for filter_name in self.filters:
            self.filters[filter_name].label = self.filters[filter_name].label.capitalize()
            if 'help_text' in self.filters[filter_name].extra:
                self.filters[filter_name].extra['help_text'] = self.filters[filter_name].extra['help_text'].capitalize()

    def get_active(self, queryset, field_name, value):
        if value:
            return queryset.filter(Q(end_date__isnull=True) | Q(end_date__gte=timezone.now()))
        return queryset

    class Meta:
        model = Campaign
        fields = ['name', 'summary', 'system', 'place', 'owner']
        form = CampaignFilterForm
