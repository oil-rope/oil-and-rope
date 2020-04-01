import logging
from concurrent.futures.thread import ThreadPoolExecutor
from smtplib import SMTPAuthenticationError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Button, ButtonHolder, Column, Div, Field, Layout, Row, Submit
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UsernameField
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from bot.models import DiscordUser

LOGGER = logging.getLogger(__name__)


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
                            '<a class="col-lg-8 btn-link" href="#no-url">{text}</a>'.format(
                                text=_('Forgot password?')
                            )
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
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.request = request
        self.setup()
        self.helper = FormHelper(self)
        self.helper.id = 'registerForm'
        self.helper.form_class = 'container-fluid'
        self.helper.layout = Layout(
            Row(
                Column(
                    Field('username', css_class=self.custom_classes),
                    css_class='col-12 col-md-6'
                ),
                Column(
                    Field('email', css_class=self.custom_classes),
                    css_class='col-12 col-md-6'
                ),
                Column(
                    Field('password1', css_class=self.custom_classes),
                    css_class='col-12 col-md-6'
                ),
                Column(
                    Field('password2', css_class=self.custom_classes),
                    css_class='col-12 col-md-6'
                )
            ),
            Row(
                Field('discord_id', css_class=self.custom_classes),
                Button('search', _('Look for user!'),
                       css_class=self.button_classes + ' align-self-center', css_id='btn_discord_invite'),
                css_class='justify-content-between'
            ),
            ButtonHolder(
                Submit('submit', _('Register'), css_class=self.submit_classes)
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

    def clean_discord_id(self):
        """
        Checks if Discord User is created.
        """

        data = self.cleaned_data.get('discord_id')

        if data:
            if not DiscordUser.objects.filter(pk=data).exists():
                msg = '{} {}'.format(_('User not found.'), _('Have you requested invitation?'))
                self.add_error('discord_id', msg)
        return data

    def get_discord_user(self):
        """
        Looks for `discord_id` field and returns :class:`DiscordUser` instance or `None`.
        """

        discord_user = None
        discord_id = self.cleaned_data.get('discord_id')
        if discord_id:
            discord_user = DiscordUser.objects.get(pk=discord_id)
        return discord_user

    def save(self, commit=True):
        """
        Before saving the instance it sets it to inactive until the user confirms email.

        Returns
        -------
        instance: User instance created.
            The user created.
        """

        instance = super(SignUpForm, self).save(commit=False)
        # Set active to False until user acitvates email
        instance.is_active = False
        # Checks for DiscordUser
        discord_user = self.get_discord_user()
        if commit:
            instance.save()
            # Adds foreing key if exists
            if discord_user:
                discord_user.user = instance
                discord_user.save()
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
