import django_filters as filters
from django.apps import apps
from django.db.models import Q
from django.forms.widgets import CheckboxInput
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from common.constants import models
from common.filters.forms import BasicFilterForm
from common.filters.mixins import FilterCapitalizeMixin
from common.forms.widgets import DateWidget

from ..enums import RoleplaySystems

Campaign = apps.get_model(models.ROLEPLAY_CAMPAIGN)
Session = apps.get_model(models.ROLEPLAY_SESSION)


class CampaignFilter(FilterCapitalizeMixin, filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    summary = filters.CharFilter(field_name='summary', lookup_expr='icontains')
    place = filters.CharFilter(field_name='place__name', lookup_expr='icontains')
    owner = filters.CharFilter(field_name='owner__username', lookup_expr='iexact')
    active = filters.BooleanFilter(
        field_name='end_date', method='get_active', label=_('active'),
        help_text=_('search only for active campaigns'), widget=CheckboxInput,
    )

    def get_active(self, queryset, field_name, value):
        if value:
            return queryset.filter(Q(end_date__isnull=True) | Q(end_date__gte=timezone.now()))
        return queryset

    class Meta:
        model = Campaign
        fields = ['name', 'summary', 'system', 'place', 'owner']
        form = BasicFilterForm


class SessionFilter(FilterCapitalizeMixin, filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    plot = filters.CharFilter(field_name='plot', lookup_expr='icontains')
    place = filters.CharFilter(field_name='campaign__place__name', lookup_expr='contains')
    system = filters.ChoiceFilter(field_name='campaign__system', choices=RoleplaySystems.choices)
    next_game = filters.DateFilter(
        field_name='next_game', lookup_expr='date__gte', widget=DateWidget,
    )
    active = filters.BooleanFilter(
        field_name='next_game', method='get_active', label=_('active'),
        help_text=_('search only for active sessions'), widget=CheckboxInput,
    )

    def get_active(self, queryset, field_name, value):
        if value:
            return queryset.filter(Q(next_game__isnull=True) | Q(next_game__gte=timezone.now()))
        return queryset

    class Meta:
        model = Session
        fields = ['campaign', 'name', 'plot', 'system', 'place', 'next_game', 'active']
        form = BasicFilterForm
