import logging
from concurrent.futures.thread import ThreadPoolExecutor
from smtplib import SMTPAuthenticationError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Button, ButtonHolder, Column, Field, Layout, Row, Submit
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UsernameField
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

LOGGER = logging.getLogger(__name__)


class LoginForm(AuthenticationForm):
    """
    Custom form to render with Crispy.
    """

    custom_classes = 'bg-transparent border-extra border-top-0 border-right-0 border-left-0 border-bottom rounded-0'

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.id = 'loginForm'
        self.helper.form_class = 'container-fluid'
        self.helper.layout = Layout(
            Row(
                Column(
                    Field(
                        'username',
                        placeholder=_('Username'),
                        css_class=self.custom_classes,
                    ),
                    css_class='col-12'
                ),
            ),
            Row(
                Column(
                    Field(
                        'password',
                        placeholder=_('Password'),
                        css_class=self.custom_classes,
                    ),
                    css_class='col-12'
                ),
            ),
            Row(
                Column(
                    Submit('login', _('Login'), css_class='btn-extra w-100'),
                    css_class='col-12 col-lg-6'
                ),
                Column(
                    HTML(
                        '<a class="col-lg-8 btn-link" href="{url}">{text}</a>'.format(
                            url=reverse('registration:resend_email'),
                            text=_('Send confirmation email')
                        ),
                    ),
                    css_class='col-12 col-lg-6'
                ),
            ),
        )

        self._clean_labels()

    def _clean_labels(self):
        for field in self.fields:
            self.fields[field].label = ''


class SignUpForm(UserCreationForm):
    """
    User registration form.
    """

    button_classes = 'btn btn-info'
    custom_classes = 'bg-transparent border-extra border-top-0 border-right-0 border-left-0 border-bottom rounded-0'
    submit_classes = 'btn btn-extra btn-lg'

    discord_id = forms.CharField(
        label=_('Discord Identifier'),
        max_length=254,
        required=False,
        help_text=_('If you have a Discord Account you want to link with just give us your ID!')
    )

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.setup()
        self.helper = FormHelper(self)
        self.helper.id = 'registerForm'
        self.helper.form_class = 'container-fluid'
        self.helper.layout = Layout(
            Row(
                Column(
                    Field('username', css_class=self.custom_classes),
                    css_class='col-12 col-lg-6 col-xl-5'
                ),
                Column(
                    Field('email', css_class=self.custom_classes),
                    css_class='col-12 col-lg-6 col-xl-5'
                ),
                css_class='justify-content-xl-between'
            ),
            Row(
                Column(
                    Field('password1', css_class=self.custom_classes),
                    css_class='col-12 col-lg-6 col-xl-5'
                ),
                Column(
                    Field('password2', css_class=self.custom_classes),
                    css_class='col-12 col-lg-6 col-xl-5'
                ),
                css_class='justify-content-xl-between'
            ),
            Row(
                Column(
                    Field('discord_id', css_class=self.custom_classes),
                    css_class='col-12 col-md-8 col-lg-6 col-xl-5'
                ),
                Column(
                    Button('search', _('Send invitation') + '!', css_class=self.button_classes + ' w-100'),
                    css_class='col-12 col-md-4 col-xl-5 align-self-center'
                ),
                css_class='justify-content-lg-between'
            ),
            Row(
                Column(
                    Submit('submit', _('Register'), css_class=self.submit_classes + ' w-100'),
                    css_class='col-12 col-xl-6'
                ),
                css_class='mt-4 mt-md-0 mt-xl-5 justify-content-xl-center'
            )
        )

    def clean_email(self):
        """
        Checks if email already exists!
        """

        data = self.cleaned_data.get('email')
        if get_user_model().objects.filter(email=data).exists():
            msg = _('This email is already in use') + '.'
            self.add_error('email', msg)
        return data

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

    def _generate_token(self, user) -> str:
        """
        Generates a token for the user to confirm it's email.

        Parameters
        ----------
        user: User instance
            The user associated to this token.

        Returns
        -------
        token: :class:`str`
            The token generated.
        """

        token = PasswordResetTokenGenerator()
        token = token.make_token(user)
        return token

    def _send_email_confirmation(self, user):
        """
        Sends a confirmation email to the user.
        """

        msg_html = render_to_string('email_templates/confirm_email.html', {
            # We declare localhost as default for tests purposes
            'domain': self.request.META.get('HTTP_HOST', 'http://localhost'),
            'token': self._generate_token(user),
            'object': user
        })

        try:
            user.email_user(_('Welcome to Oil & Rope!'), '', html_message=msg_html)
        except SMTPAuthenticationError:
            LOGGER.exception('Unable to logging email server with given credentials.')

    def save(self, commit=True):
        """
        Before saving the instance it sets it to inactive until the user confirms email.

        Returns
        -------
        instance: User instance created.
            The user created.
        """

        instance = super().save(commit=False)
        # Set active to False until user acitvates email
        instance.is_active = False
        if commit:
            instance.save()
            # User shouldn't wait for the email to be sent
            with ThreadPoolExecutor(max_workers=2) as executor:
                executor.submit(self._send_email_confirmation, instance)
        return instance

    class Meta:
        model = get_user_model()
        fields = ('username', 'email')
        field_classes = {'username': UsernameField}
        help_texts = {
            'email': _('We will send you an email to confirm your account') + '.'
        }


class ResendEmailForm(forms.Form):
    """
    Checks for given email in database.
    """

    custom_classes = 'bg-transparent border-extra border-top-0 border-right-0 border-left-0 border-bottom rounded-0'
    submit_classes = 'btn btn-extra btn-lg'

    email = forms.EmailField(
        label=_('Email address'),
        help_text=_('Enter your email address and we\'ll resend you the confirmation email') + '.',
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class = 'container-fluid'
        self.helper.layout = Layout(
            Row(
                Field('email', css_class=self.custom_classes),
                css_class='justify-content-sm-center'
            ),
            ButtonHolder(
                Submit('submit', _('Resend email'), css_class=self.submit_classes + ' col-12 col-sm-6'),
                css_class='d-sm-flex justify-content-sm-center'
            )
        )

    def clean_email(self):
        data = self.cleaned_data.get('email')
        if not get_user_model().objects.filter(email=data).exists():
            msg = _('This email doesn\'t belong to a user') + '.'
            self.add_error('email', msg)
        return data
