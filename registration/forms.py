from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Field, Layout, Submit
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext
from django.utils.translation import ugettext_lazy as _


class LoginForm(AuthenticationForm):
    """
    Custom form to render with Crispy.
    """

    custom_classes = 'bg-transparent border-extra border-top-0 border-right-0 border-left-0 border-bottom rounded-0'

    def __init__(self, request=None, *args, **kwargs):
        super(LoginForm, self).__init__(request=request, *args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.id = 'loginForm'
        self.helper.form_class = 'container-fluid'
        self.helper.layout = Layout(
            Div(
                Field(
                    'username',
                    placeholder=_('Username'),
                    css_class=self.custom_classes,
                ),
                Field(
                    'password',
                    placeholder=_('Password'),
                    css_class=self.custom_classes,
                ),
                Div(
                    Div(
                        HTML(
                            '<a class="col-lg-8 btn-link" href="#no-url">' + gettext('Forgot password?') + '</a>'
                        ),
                        Submit('', _('Login'), css_class='btn btn-extra col-lg-4'),
                        css_class='row align-items-lg-center justify-content-lg-between'
                    ),
                    css_class='container-fluid'
                ),
                css_class='row flex-column'
            )
        )

        self._clean_labels()

    def _clean_labels(self):
        for field in self.fields:
            self.fields[field].label = ''
