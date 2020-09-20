import logging
from concurrent.futures.thread import ThreadPoolExecutor
from smtplib import SMTPAuthenticationError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Column, Div, Layout, Row, Submit
from django import forms
from django.conf import settings
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from bot.models import DiscordUser

LOGGER = logging.getLogger(__name__)


class LoginForm(auth_forms.AuthenticationForm):
    """
    Custom form to render with Crispy.
    """

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'loginForm'
        self.helper.field_class = 'form-text-white'
        self.helper.label_class = 'text-white'
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='col-12'),
                Column('password', css_class='col-12'),
            ),
            Row(
                Column(
                    Submit('login', _('Login'), css_class='btn btn-lg text-white w-100'),
                    css_class='col-6'
                ),
                Column(
                    Div(
                        Row(
                            HTML(
                                '<a class="mr-lg-5" href="{url}">{text}</a>'.format(
                                    url=reverse('registration:password_reset'),
                                    text=_('Forgot password?')
                                )
                            ),
                            HTML(
                                '<a class="" href="{url}">{text}</a>'.format(
                                    url=reverse('registration:resend_email'),
                                    text=_('Resend email')
                                )
                            ),
                            css_class='row justify-content-sm-between justify-content-lg-center \
                                        align-items-center h-100'
                        ),
                        css_class='container-fluid h-100'
                    ),
                    css_class='col-6'
                ),
            ),
        )


class SignUpForm(auth_forms.UserCreationForm):
    """
    User registration form.
    """

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
        self.consumer_url = self._resolve_consumer_url()
        self.send_invitation_url = reverse('bot:utils:send_invitation')
        self.helper = FormHelper(self)
        self.helper.id = 'registerForm'
        self.helper.form_class = 'container-fluid'
        self.helper.layout = Layout(
            Row(
                Column(
                    'username',
                    css_class='col-12 col-lg-6 col-xl-5'
                ),
                Column(
                    'email',
                    css_class='col-12 col-lg-6 col-xl-5'
                ),
                css_class='justify-content-xl-between'
            ),
            Row(
                Column(
                    'password1',
                    css_class='col-12 col-lg-6 col-xl-5'
                ),
                Column(
                    'password2',
                    css_class='col-12 col-lg-6 col-xl-5'
                ),
                css_class='justify-content-xl-between'
            ),
            Row(
                Column(
                    'discord_id',
                    css_class='col-12 col-md-8 col-lg-6 col-xl-5'
                ),
                Column(
                    Div(
                        # Refers to ReactComponent `UserCheckButton`
                        data_consumer_url=self.consumer_url,
                        data_invitation_url=settings.BOT_INVITATION,
                        data_send_invitation_url=self.send_invitation_url,
                        data_related_field='id_discord_id',
                        css_id='discord_check_user'
                    ),
                    css_class='col-12 col-md-4 col-xl-5 align-self-center',
                ),
                css_class='justify-content-lg-between'
            ),
            Row(
                Column(
                    Submit('submit', _('Register'), css_class='btn-lg w-100'),
                    css_class='col-12 col-xl-6'
                ),
                css_class='mt-4 mt-md-0 mt-xl-5 justify-content-xl-center'
            )
        )

    def _resolve_consumer_url(self):
        consumer_url = 'wss://' if self.request.is_secure() else 'ws://'
        consumer_url += settings.WS_HOST if settings.WS_HOST else self.request.get_host()
        consumer_url += reverse('bot_ws:register')
        return consumer_url

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
            required_fields = ('email',)
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
        except SMTPAuthenticationError:  # pragma: no cover
            LOGGER.exception('Unable to logging email server with given credentials.')

    def clean_discord_id(self):
        """
        Checks if Discord User is created.
        """

        data = self.cleaned_data.get('discord_id')

        if data:
            if not DiscordUser.objects.filter(pk=data).exists():
                msg = '{}. {}'.format(_('User not found'), _('Have you requested invitation?'))
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

        instance = super().save(commit=False)
        # Set active to False until user activates email
        instance.is_active = False
        # Checks for DiscordUser
        discord_user = self.get_discord_user()
        if commit:
            instance.save()
            # Adds foreign key if exists
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
        field_classes = {'username': auth_forms.UsernameField}
        help_texts = {
            'email': _('We will send you an email to confirm your account') + '.'
        }


class ResendEmailForm(forms.Form):
    """
    Checks for given email in database.
    """

    email = forms.EmailField(
        label=_('Email address'),
        help_text=_('Enter your email address and we\'ll resend you the confirmation email') + '.',
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(
                Column('email', css_class='col-12 col-xl-8'),
                css_class='justify-content-around'
            ),
            Row(
                Column(
                    Submit('submit', _('Resend email'), css_class='w-100'),
                    css_class='col-md-10 col-lg-6'
                ),
                css_class='justify-content-md-around'
            )
        )

    def clean_email(self):
        data = self.cleaned_data.get('email')
        if not get_user_model().objects.filter(email=data).exists():
            msg = _('This email doesn\'t belong to a user') + '.'
            self.add_error('email', msg)
        return data


class PasswordResetForm(auth_forms.PasswordResetForm):
    """
    This forms allows a user to resets its password.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        msg = '{}.'.format(_('We will send you a recovery link to this email'))
        self.add_help_text('email', msg)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(
                Column('email')
            ),
            Row(
                Column(
                    Submit('submit', _('Send email'), css_class='w-100')
                )
            )
        )

    def add_help_text(self, field, help_text):
        self.fields[field].help_text = help_text

    def clean_email(self):
        data = self.cleaned_data.get('email')
        if not get_user_model().objects.filter(email=data).exists():
            msg = _('This email doesn\'t belong to a user') + '.'
            self.add_error('email', msg)
        return data


class SetPasswordForm(auth_forms.SetPasswordForm):
    """
    Allows the user to change the password.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(
                Column('new_password1', css_class='col-12 col-lg-5'),
                Column('new_password2', css_class='col-12 col-lg-5'),
                css_class='justify-content-around'
            ),
            Row(
                Column(
                    Submit('submit', _('Change password'), css_class='w-100'),
                    css_class='col-12 col-lg-6'
                ),
                css_class='justify-content-around'
            )
        )
