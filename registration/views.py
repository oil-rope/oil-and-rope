from django.contrib.auth import views as auth_views


class LoginView(auth_views.LoginView):
    """
    View that handles login form.
    """
