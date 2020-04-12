import logging
from smtplib import SMTPAuthenticationError

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import views as auth_views
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, FormView, RedirectView

from . import forms
from .mixins import RedirectAuthenticatedUserMixin

LOGGER = logging.getLogger(__name__)


class LoginView(auth_views.LoginView):
    """
    View that handles login form.
    """

    authentication_form = forms.LoginForm

    def form_invalid(self, form):
        response = super(LoginView, self).form_invalid(form)
        cleaned_data = form.cleaned_data
        try:
            user = get_user_model().objects.get(username=cleaned_data['username'])
            if not user.is_active:
                warn_message = '{}. {}'.format(
                    _('Seems like this user is inactive'),
                    _('Have you confirmed your email?')
                )
                messages.warning(self.request, warn_message)
        except get_user_model().DoesNotExist:
            LOGGER.warning('Attemp to access an inexistent user, we assume username is just incorrect.')
        finally:
            return response


class SignUpView(RedirectAuthenticatedUserMixin, CreateView):
    """
    View for registering a new user.
    """

    model = get_user_model()
    form_class = forms.SignUpForm
    template_name = 'registration/register.html'
    succes_message = None
    success_url = reverse_lazy('registration:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_success_message(self) -> str:
        if self.succes_message:  # pragma: no cover
            return self.succes_message
        succes_message = '{}! {}.'.format(
            _('User created'),
            _('Please confirm your email')
        )
        return succes_message

    def get_form_kwargs(self):
        kwargs = super(SignUpView, self).get_form_kwargs()
        kwargs.update({
            'request': self.request
        })
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, self.get_success_message())
        return redirect(self.success_url)


class ActivateAccountView(RedirectAuthenticatedUserMixin, RedirectView):
    """
    Gets token and redirects user after activating it.
    """

    url = reverse_lazy('registration:login')

    def get_user(self):
        """
        Gets and returns user model.

        Returns
        -------
        user: Instance
            The user instance.
        """

        primary_key = self.kwargs['pk']
        user = get_user_model().objects.get(pk=primary_key)
        return user

    def get_token(self) -> str:
        """
        Gets and returns the given token.

        Returns
        -------
        token: :class:`str`
            The token to validate.
        """

        token = self.kwargs['token']
        return token

    def validate_token(self) -> bool:
        """
        Validates if given token is correct for the user.

        Returns
        -------
        validation: :class:`bool`
            True if token belongs to user.
        """

        self.user = self.get_user()
        token = self.get_token()

        token_validator = PasswordResetTokenGenerator()
        return token_validator.check_token(self.user, token)

    def get(self, request, *args, **kwargs):
        if self.validate_token():
            self.user.is_active = True
            self.user.save()
            messages.success(request, _('Your email has been confirmed') + '!')
        return super(ActivateAccountView, self).get(request, *args, **kwargs)


class ResendConfirmationEmailView(RedirectAuthenticatedUserMixin, FormView):
    """
    In case user needs the email to be resend we create this view.
    """

    template_name = 'registration/resend_email.html'
    form_class = forms.ResendEmailForm
    success_message = None
    success_url = reverse_lazy('registration:login')

    def get_user(self, email):
        try:
            user = get_user_model().objects.get(email=email)
            return user
        except get_user_model().MultipleObjectsReturned as ex:
            LOGGER.exception('Multiple users with same email found.')
            raise ex

    def generate_token(self, user) -> str:
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

    def send_email(self, user):
        """
        Resends a confirmation email to the user.
        """

        msg_html = render_to_string('email_templates/confirm_email.html', {
            # We declare localhost as default for tests purposes
            'domain': self.request.META.get('HTTP_HOST', 'http://localhost'),
            'token': self.generate_token(user),
            'object': user
        })

        try:
            user.email_user(_('Welcome to Oil & Rope!'), '', html_message=msg_html)
        except SMTPAuthenticationError:  # pragma: no cover
            LOGGER.exception('Unable to logging email server with given credentials.')

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        try:
            user = self.get_user(cleaned_data['email'])
            self.send_email(user)
            messages.success(self.request, _('Your confirmation email has been sent') + '!')
            return super().form_valid(form)
        except get_user_model().MultipleObjectsReturned:
            messages.warning(self.request, _('Multiple users with same email, please contact our developers'))
            return super().form_invalid(form)
