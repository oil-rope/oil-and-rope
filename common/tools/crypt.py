from django.core.signing import Signer, TimestampSigner


def get_token(value: str, signer: Signer or TimestampSigner = None) -> str:
    """
    Generate a token from a string.
    This token can be decrypted by `dja.core.signing.Signer.unsign`.

    Parameters
    ----------
    value: :class:`str`
        The string to be encrypted.
    signer: :class:`~django.core.signing.Signer` or :class:`~django.core.signing.TimestampSigner`
        The signer to be used.

    Returns
    -------
    :class:`str`
        The encrypted string.
    """

    if not signer:
        signer = Signer()
    return signer.sign(value)
