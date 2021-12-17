from crispy_forms import bootstrap, layout
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy as _p

from common.forms import layout as common_layout


class DynamicMenuLayout(layout.Layout):
    def __init__(self):
        super().__init__(
            bootstrap.TabHolder(
                bootstrap.Tab(
                    _p('noun', 'naming').title(),
                    layout.Row(
                        layout.Column('prepended_text', css_class='col-12 col-md-4'),
                        layout.Column('name', css_class='col-12 col-md-4'),
                        layout.Column('appended_text', css_class='col-12 col-md-4'),
                        layout.Div(
                            css_id='menuDisplayNameContainer',
                            css_class='col-12 col-md-12 bg-light',
                            style='min-height: 50px'
                        ),
                        layout.Column('description', css_class='col-12'),
                    ),
                ),
                bootstrap.Tab(
                    _('direction').title(),
                    layout.Row(
                        layout.Column('url_resolver', css_class='col-12 col-md-6'),
                        layout.Column('extra_urls_args', css_class='col-12 col-md-6'),
                        layout.Div(
                            css_id='menuDisplayURLResolver',
                            css_class='col-12 col-md-12 bg-light',
                            style='min-height: 50px'
                        ),
                    ),
                ),
                bootstrap.Tab(
                    _('permissions').title(),
                    layout.Row(
                        layout.Column('permissions_required', css_class='col-12 col-md-6 col-lg-4'),
                        layout.Column('related_models', css_class='col-12 col-md-6 col-lg-4'),
                    ),
                    layout.Row(
                        layout.Column('staff_required', css_class='col'),
                    )
                ),
                bootstrap.Tab(
                    _('submenu configuration').title(),
                    layout.Row(
                        layout.Column('parent', css_class='col-md-4'),
                        layout.Column('menu_type', css_class='col-md-4'),
                        layout.Column('order', css_class='col-md-4'),
                    ),
                )
            ),
            layout.Row(
                layout.Column(
                    common_layout.SubmitClearLayout(
                        submit_css_class='col-12 col-md-5',
                        reset_css_class='col-12 col-md-5',
                    ),
                ),
                css_class='mt-5'
            ),
        )
