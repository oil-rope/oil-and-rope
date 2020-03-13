from django.contrib.auth import views as auth_views, get_user_model

from django.views.generic import CreateView
from . import forms


class LoginView(auth_views.LoginView):
    """
    View that handles login form.
    """

    authentication_form = forms.LoginForm

class SignUpView(CreateView):
    """
    View for registering a new user.
    """

    model = get_user_model()
    form_class = forms.SignUpForm
    template_name = 'registration/register.html'

