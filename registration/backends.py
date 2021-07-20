from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username, password, **kwargs)

        # If username is not and email is not even worth try
        if '@' not in username:
            return user

        try:
            # Little trick to just get username from existing user
            user = get_user_model().objects.get(email=username)
            username = user.username
            user = super().authenticate(request, username, password, **kwargs)
        except get_user_model().DoesNotExist:
            return
        finally:
            return user
