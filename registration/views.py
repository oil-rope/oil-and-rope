from django.contrib.auth import views as auth_views

from . import forms


class LoginView(auth_views.LoginView):
    """
    View that handles login form.
    """

    form_class = forms.LoginForm
