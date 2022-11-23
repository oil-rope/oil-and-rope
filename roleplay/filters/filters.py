import django_filters as filters
from django.db.models import Q, QuerySet
from django.forms.widgets import CheckboxInput
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from common.filters.forms import BasicFilterForm
from common.filters.mixins import FilterCapitalizeMixin
from common.forms.widgets import DateWidget
from roleplay.models import Campaign, Race, Session

from ..enums import RoleplaySystems
from .enums import AbilitiesEnum


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


class RaceFilter(FilterCapitalizeMixin, filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    description = filters.CharFilter(lookup_expr='icontains')
    campaign = filters.CharFilter(lookup_expr='name__icontains')
    place = filters.CharFilter(lookup_expr='name__icontains')
    ability_modifiers = filters.MultipleChoiceFilter(
        field_name='ability_modifiers', method='get_ability_modifiers', label=_('ability modifiers'),
        help_text=_('search for races that have ability modifiers'), choices=AbilitiesEnum.choices,
    )

    def get_ability_modifiers(self, queryset: QuerySet, field_name: str, values: list[str]):
        if values:
            for ability in values:
                queryset = queryset.filter(~Q(**{ability: 0}))
            return queryset
        return queryset

    class Meta:
        model = Race
        fields = [
            'name', 'description', 'campaign', 'place', 'affected_by_armor',
        ]
        form = BasicFilterForm
