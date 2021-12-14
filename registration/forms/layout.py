from crispy_forms import layout
from django.shortcuts import reverse
from django.utils.translation import gettext_lazy as _

from common.forms import layout as common_layout


class LoginFormLayout(layout.Layout):
    def __init__(self, *args, **kwargs):
        super().__init__(
            layout.Layout(
                layout.Row(
                    layout.Column('username', css_class='col-sm-12 col-md-10 col-lg-8 col-xl-10'),
                    layout.Column('password', css_class='col-sm-12 col-md-10 col-lg-8 col-xl-10'),
                    css_class='justify-content-md-around',
                ),
                layout.Row(
                    layout.Submit('login', _('login').capitalize(), css_class='col col-md-9 btn-lg text-white'),
                    layout.Div(css_class='w-100'),
                    common_layout.Link(
                        content=_('login with %(social_media)s').capitalize() % {'social_media': 'Google'},
                        url=reverse('google_login'),
                        css_class='btn-lg bg-white col col-md-9 mt-2',
                    ),
                    css_class='justify-content-md-around mt-md-3',
                )
            )
        )
