import logging
import re
from smtplib import SMTPException

from crispy_forms.helper import FormHelper
from django import forms
from django.apps import apps
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from bot.exceptions import DiscordApiException
from bot.models import User
from common.constants import models
from common.utils.auth import generate_token

from .layout import (LoginFormLayout, PasswordResetFormLayout, ResendEmailFormLayout, SetPasswordFormLayout,
                     SignUpFormLayout)

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
        self.helper.form_method = 'POST'
        self.helper.form_action = 'registration:login'
        self.helper.include_media = False
        self.helper.field_class = 'form-text-white'
        self.helper.label_class = 'text-white'
        self.helper.form_id = 'formLogin'
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

        # NOTE: Using `.title()`, `capitalize()` or any string methods into variable declaration results
        # into not translating the field.
        discord_id_field = self.fields['discord_id']
        discord_id_field.label = discord_id_field.label.title()
        discord_id_field.help_text = discord_id_field.help_text.capitalize()

        self.request = request
        self.helper = FormHelper(self)
        self.helper.form_action = 'registration:register'
        self.helper.include_media = False
        self.helper.id = 'registerForm'
        self.helper.layout = SignUpFormLayout()

    def clean_discord_id(self):
        data = self.cleaned_data.get('discord_id')
        if data:
            if re.match(r'.+#\d+', data):
                msg = _('seems like that\'s your discord discriminator not your identifier.').capitalize()
                msg += ' ' + _('right click on your user and then click on %(popup_msg)s.').capitalize() % {
                    'popup_msg': 'Copy ID'
                }
                raise ValidationError(msg)
            try:
                data = User(data)
            except DiscordApiException:
                msg = _('seems like your user couldn\'t be found, do you have any server in common with our bot?')
                raise ValidationError(msg.capitalize())

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

        title = 'Oil & Rope'
        subject = _('welcome to %(title)s!') % {'title': title}
        send_mail(
            subject=str(subject).capitalize(), message='', from_email=None,
            recipient_list=[user.email], html_message=html_msg,
        )

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
            try:
                self._send_email_confirmation(instance)
            # NOTE: ConnectionError is when SMTP server is unreachable, SMTPException is for credentials, bad format...
            except (ConnectionError, SMTPException) as ex:
                LOGGER.exception(ex)
                instance.delete()
                raise ex
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

        email_field = self.fields['email']
        email_field.label = email_field.label.capitalize()
        email_field.help_text = email_field.help_text.capitalize()

        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.form_action = 'registration:resend_email'
        self.helper.include_media = False
        self.helper.layout = ResendEmailFormLayout()

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
        self.helper.layout = PasswordResetFormLayout()

    def add_help_text(self, field, help_text):
        self.fields[field].help_text = help_text

    def clean_email(self):
        data = self.cleaned_data.get('email')
        if not get_user_model().objects.filter(email=data).exists():
            msg = _('this email doesn\'t belong to a user.').capitalize()
            self.add_error('email', msg)
        return data


class SetPasswordForm(auth_forms.SetPasswordForm):
    """
    Allows the user to change the password.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = SetPasswordFormLayout()


class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'

    class Meta:
        model = apps.get_model(models.USER_MODEL)
        fields = (
            'username', 'first_name', 'last_name', 'email',
        )
