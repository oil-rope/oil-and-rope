import logging
from smtplib import SMTPAuthenticationError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Column, Layout, Row, Submit
from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from bot.exceptions import DiscordApiException
from bot.models import User
from common.utils.auth import generate_token

from .layout import LoginFormLayout, SignUpFormLayout

LOGGER = logging.getLogger(__name__)


class LoginForm(auth_forms.AuthenticationForm):
    """
    Custom form to render with Crispy.
    """

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)

        # Changing Username label on the go
        username_label = _('username or email').capitalize()
        self.fields['username'].label = username_label

        self.helper = FormHelper(self)
        self.helper.field_class = 'form-text-white'
        self.helper.label_class = 'text-white'
        self.helper.form_method = 'POST'
        self.helper.form_action = reverse('registration:login')
        self.helper.form_id = 'formLogin'
        self.helper.include_media = False
        self.helper.layout = LoginFormLayout()


class SignUpForm(auth_forms.UserCreationForm):
    """
    User registration form.
    """

    discord_id = forms.CharField(
        label=_('discord identifier'),
        max_length=254,
        required=False,
        help_text=_('if you have a discord account you want to link with just give us your ID!')
    )

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.send_invitation_url = reverse('bot:utils:send_invitation')
        self.helper = FormHelper(self)
        self.helper.form_action = reverse('registration:register')
        self.helper.id = 'registerForm'
        self.helper.layout = SignUpFormLayout()

    def clean_discord_id(self):
        data = self.cleaned_data.get('discord_id')
        if data:
            try:
                data = User(data)
            except DiscordApiException:
                msg = _('seems like your user couldn\'t be found, do you have any server in common with our bot?')
                msg = msg.capitalize()
                raise ValidationError(msg)

        return data

    def _send_email_confirmation(self, user):
        """
        Sends a confirmation email to the user.
        """

        html_msg = render_to_string('email_templates/confirm_email.html', {
            # We declare localhost as default for tests purposes
            'domain': self.request.META.get('HTTP_HOST', 'http://localhost'),
            'token': generate_token(user),
            'object': user
        })

        try:
            title = 'Oil & Rope'
            subject = _('welcome to %(title)s!') % {'title': title}
            send_mail(
                subject=str(subject).capitalize(), message='', from_email=None,
                recipient_list=[user.email], html_message=html_msg,
            )
        except SMTPAuthenticationError:  # pragma: no cover
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
        # Set active to False until user activates email
        instance.is_active = False
        if commit:
            instance.save()
            self._send_email_confirmation(instance)
        return instance

    class Meta:
        model = get_user_model()
        fields = ('username', 'email')
        field_classes = {'username': auth_forms.UsernameField}
        help_texts = {
            'email': _('we will send you an email to confirm your account.')
        }


class ResendEmailForm(forms.Form):
    """
    Checks for given email in database.
    """

    email = forms.EmailField(
        label=_('email address'),
        help_text=_('enter your email address and we\'ll resend you the confirmation email.'),
        required=True,
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
                    Submit('submit', _('resend email').capitalize(), css_class='w-100'),
                    css_class='col-md-10 col-lg-6'
                ),
                css_class='justify-content-md-around'
            )
        )

    def clean_email(self):
        data = self.cleaned_data.get('email')
        if not get_user_model().objects.filter(email=data).exists():
            msg = _('this email doesn\'t belong to a user.').capitalize()
            self.add_error('email', msg)
        return data


class PasswordResetForm(auth_forms.PasswordResetForm):
    """
    This forms allows a user to resets its password.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        msg = _('we will send you a recovery link to this email.').capitalize()
        self.add_help_text('email', msg)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(
                Column('email')
            ),
            Row(
                Column(
                    Submit('submit', _('send email').capitalize(), css_class='w-100')
                )
            )
        )

    def add_help_text(self, field, help_text):
        self.fields[field].help_text = help_text

    def clean_email(self):
        data = self.cleaned_data.get('email')
        if not get_user_model().objects.filter(email=data).exists():
            msg = _('this email doesn\'t belong to a user').capitalize() + '.'
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
                    Submit('submit', _('change password').capitalize(), css_class='w-100'),
                    css_class='col-12 col-lg-6'
                ),
                css_class='justify-content-around'
            )
        )
