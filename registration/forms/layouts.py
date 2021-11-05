from crispy_forms import layout
from django.utils.translation import gettext_lazy as _

LoginFormLayout = layout.Layout(
    layout.Row(
        layout.Column('username', css_class='col-sm-12 col-md-10 col-lg-8 col-xl-10'),
        layout.Column('password', css_class='col-sm-12 col-md-10 col-lg-8 col-xl-10'),
        css_class='justify-content-md-around',
    ),
    layout.Row(
        layout.Submit('login', _('login').capitalize(), css_class='col col-md-9 btn-lg text-white'),
        css_class='justify-content-md-around mt-md-3',
    ),
)
