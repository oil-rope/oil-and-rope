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
        layout.Div(css_class='w-100'),
        # TODO: There's must be a better way to do this
        # NOTE: Either 'gettext_lazt' or 'reverse' cannot be used here since it appears to load before Apps.
        layout.HTML("""
                    {% load i18n %}
                    {% load socialaccount %}
                    <a href="{% provider_login_url "google" %}" class="btn btn-lg bg-white col col-md-9 mt-2">
                      {% trans 'login with Google'|capfirst %}
                    </a>
                    """),
        css_class='justify-content-md-around mt-md-3',
    ),
)
