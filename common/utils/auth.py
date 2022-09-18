from typing import TYPE_CHECKING

from django.contrib.auth.tokens import PasswordResetTokenGenerator

if TYPE_CHECKING:  # pragma: no cover
    from registration.models import User


def generate_token(user: 'User') -> str:
    """
    Generates a token associated with a user.

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
