from django.core.signing import Signer

from common.tools.crypt import get_token


def test_get_token_without_signer():
    string = 'Hello World!'
    token = get_token(string)

    assert isinstance(token, str)
    assert token != string


def test_get_token_with_signer():
    string = 'Hello World!'
    signer = Signer()
    token = get_token(string, signer)

    assert isinstance(token, str)
    assert token != string
    assert token == signer.sign(string)
