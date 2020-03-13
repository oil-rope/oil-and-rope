from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, ButtonHolder, Div, Field, Layout, Row, Submit
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UsernameField
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


class SignUpForm(UserCreationForm):
    """
    User registration form.
    """

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.setup()
        self.helper = FormHelper(self)
        self.helper.id = 'registerForm'
        self.helper.form_class = 'container-fluid'
        self.helper.layout = Layout(
            Row(
                Field('username', wrapper_class='col-12'),
                Field('email', wrapper_class='col-12'),
                Field('password1', wrapper_class='col-12'),
                Field('password2', wrapper_class='col-12')
            ),
            ButtonHolder(
                Submit('submit', _('Register'))
            )
        )

    def setup(self, required_fields=None):
        """
        Modifies some attributtes before rendering the form.

        Parameters
        ----------
        required_fields: Iterable.
            Fields to modify and set as required.
        """

        if not required_fields:
            required_fields = ('email', )
        for field in required_fields:
            self.fields[field].required = True

    class Meta:
        model = get_user_model()
        fields = ('username', 'email')
        field_classes = {'username': UsernameField}
