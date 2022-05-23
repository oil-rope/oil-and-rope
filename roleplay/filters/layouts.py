from crispy_forms import layout
from django.utils.translation import gettext_lazy as _

from common.enums import AvailableIcons
from common.forms import layout as common_layout


class CampaignFilterLayout(layout.Layout):
    def __init__(self):
        super().__init__(
            layout.Column(
                layout.Field('name'),
                css_class='col-12 col-md-6'
            ),
            layout.Column(
                layout.Field('summary'),
                css_class='col-12 col-md-6'
            ),
            layout.Column(
                layout.Field('system'),
                css_class='col-12 col-md-6'
            ),
            layout.Column(
                layout.Field('place'),
                css_class='col-12 col-md-6'
            ),
            layout.Column(
                layout.Field('owner'),
                css_class='col-12 col-md-6'
            ),
            layout.Column(
                layout.Field('active'),
                css_class='col-12 col-md-6'
            ),
            layout.Div(css_class='w-100'),
            layout.Column(
                common_layout.Button(
                    content=_('search').capitalize(), icon=AvailableIcons.MAGNIFYING_GLASS,
                    type='submit', css_class='btn-primary w-100',
                ),
                css_class='col-12 col-md-6'
            ),
        )
