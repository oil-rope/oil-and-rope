import json

from requests.models import Response

from tests import fake


def user_response(**defaults) -> Response:
    """
    Returns a mock of a Discord User response from API.

    Parameters
    ----------
    defaults:
        Key-Value params to add to the response.
    """

    user = {
        'id': f'{fake.random_number(digits=18)}',
        'username': fake.user_name(),
        'avatar': fake.md5(),
        'avatar_decoration': None,
        'discriminator': ''.join([str(fake.pyint(min_value=1, max_value=9)) for _ in range(4)]),
        'public_flags': 0,
        'flags': 0,
        'bot': False,
        'banner': None,
        'banner_color': None,
        'accent_color': None,
        'bio': fake.sentence(),
        'locale': fake.locale(),
        'mfa_enabled': fake.pybool(),
        'email': fake.email(),
        'verified': True,
    }
    user.update(defaults)

    response = Response()
    response.headers.update({
        'Content-Type': 'application/json',
        'Transfer-Encoding': 'chunked',
        'Connection': 'keep-alive',
        'X-Content-Type-Options': 'nosniff',
        'Vary': 'Accept-Encoding',
    })
    response.status_code = 200
    response._content = json.dumps(user).encode(encoding='utf-8')

    return response
