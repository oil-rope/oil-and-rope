from django.contrib.auth.tokens import PasswordResetTokenGenerator


def generate_token(user) -> str:
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
