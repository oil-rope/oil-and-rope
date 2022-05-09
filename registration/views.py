import logging
import random
from smtplib import SMTPAuthenticationError, SMTPException

from crispy_forms import layout
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.http import HttpResponseForbidden
from django.shortcuts import resolve_url
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, FormView, RedirectView, TemplateView, UpdateView
from rest_framework.authtoken.models import Token

from common.templatetags.string_utils import capfirstletter as cfl

from . import forms, models
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
                warn_message = '{} {}'.format(
                    _('seems like this user is inactive.').capitalize(),
                    cfl(_('have you confirmed your email?')),
                )
                messages.warning(self.request, warn_message)
        except get_user_model().DoesNotExist:
            LOGGER.warning('Attempt to access a non existent user, we assume username is just incorrect.')
        finally:
            return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['slogan'] = random.choice(settings.SLOGANS)
        return context


class SignUpView(RedirectAuthenticatedUserMixin, CreateView):
    """
    View for registering a new user.
    """

    model = get_user_model()
    form_class = forms.SignUpForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('registration:auth:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_success_message(self) -> str:
        success_message = '{} {}'.format(
            cfl(_('user created!')),
            _('please confirm your email.').capitalize()
        )
        return success_message

    def get_form_kwargs(self):
        kwargs = super(SignUpView, self).get_form_kwargs()
        kwargs.update({
            'request': self.request
        })
        return kwargs

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, self.get_success_message())
        # NOTE: If SMTP is unreachable one of those exceptions will be raised
        except (ConnectionError, SMTPException):
            msg = '{} {}'.format(
                _('seems like we are experimenting issues with our mail automatization.').capitalize(),
                _('please try later.').capitalize(),
            )
            messages.error(self.request, msg)
            # NOTE: We return response as is form has failed so user doesn't have to write everything again
            response = super().form_invalid(form)
        finally:
            return response


class ActivateAccountView(RedirectAuthenticatedUserMixin, RedirectView):
    """
    Gets token and redirects user after activating it.
    """

    url = reverse_lazy('registration:auth:login')

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
            messages.success(request, cfl(_('your email has been confirmed!')))
        return super(ActivateAccountView, self).get(request, *args, **kwargs)


class ResendConfirmationEmailView(RedirectAuthenticatedUserMixin, FormView):
    """
    In case user needs the email to be resent we create this view.
    """

    template_name = 'registration/resend_email.html'
    form_class = forms.ResendEmailForm
    success_message = None
    success_url = reverse_lazy('registration:auth:login')

    def get_user(self, email):
        user = get_user_model().objects.get(email=email)
        return user

    def generate_token(self, user) -> str:
        """
        Generates a token for the user to confirm its email.

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
            msg = cfl(_('welcome to %(title)s!')) % {'title': 'Oil & Rope'}
            user.email_user(msg, '', html_message=msg_html)
        except SMTPAuthenticationError:  # pragma: no cover
            LOGGER.exception('Unable to logging email server with given credentials.')

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        user = self.get_user(cleaned_data['email'])
        self.send_email(user)
        messages.success(self.request, cfl(_('your confirmation email has been sent!')))
        return super().form_valid(form)


class ResetPasswordView(RedirectAuthenticatedUserMixin, auth_views.PasswordResetView):
    """
    Allow user to reset its password.
    """

    # Error non-reverse matching if no declared
    email_template_name = 'email_templates/password_reset_email.html'

    extra_email_context = {
        'title': _('password reset')
    }
    form_class = forms.PasswordResetForm
    html_email_template_name = 'email_templates/password_reset_email.html'
    success_url = reverse_lazy('registration:auth:login')
    template_name = 'registration/password_reset.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        msg = cfl(_('email for password reset request sent!'))
        messages.success(self.request, msg)
        return response


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    """
    Allows the user to set a new password.
    """

    form_class = forms.SetPasswordForm
    success_url = reverse_lazy('registration:auth:login')
    template_name = 'registration/password_reset_confirm.html'

    def get_success_url(self):
        msg = cfl(_('password changed successfully!'))
        messages.success(self.request, msg)
        return super().get_success_url()


class PasswordChangeView(auth_views.PasswordChangeView):
    form_class = forms.SetPasswordForm
    template_name = 'registration/password_change.html'

    def get_success_url(self):
        msg = cfl(_('password changed successfully!'))
        messages.success(self.request, msg)
        return resolve_url(self.request.user)


class RequestTokenView(LoginRequiredMixin, TemplateView):
    template_name = 'api/request_token.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        token, created = Token.objects.get_or_create(user=self.request.user)
        context_data['object'] = token
        context_data['created'] = created
        return context_data


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = models.User
    form_class = forms.UserForm
    template_name = 'registration/user_update.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        if self.get_object() == request.user:
            return super().dispatch(request, *args, **kwargs)
        return HttpResponseForbidden()

    def get_initial(self):
        initial = super().get_initial()
        profile = self.request.user.profile
        initial.update({
            'bio': profile.bio,
            'birthday': profile.birthday,
            'language': profile.language,
            'web': profile.web,
        })
        if profile.image:
            initial.update({'image': profile.image})
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        profile = self.object.profile
        if profile.image:
            src = profile.image.url
        else:
            src = f'{settings.STATIC_URL}img/default_user.png'
        alt_text = _('avatar').capitalize()
        img_element = layout.HTML(
            f'<img alt="{alt_text}" class="rounded-circle" src="{src}" style="width: 250px; height: 200px" />'
        )
        form.helper.layout[0][1][0].insert(0, img_element)
        return form

    def get_success_url(self):
        return resolve_url('registration:user:edit', pk=self.object.pk)

    def form_valid(self, form):
        res = super().form_valid(form)
        msg = cfl(_('user updated successfully!'))
        messages.success(self.request, msg)
        self.request.session['session_language'] = self.object.profile.language
        return res
