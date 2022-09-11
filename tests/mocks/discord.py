import copy
import json

from requests.models import Response

from tests import fake

_base_response = Response()
_base_response.headers.update({
    'Content-Type': 'application/json',
    'Transfer-Encoding': 'chunked',
    'Connection': 'keep-alive',
    'X-Content-Type-Options': 'nosniff',
    'Vary': 'Accept-Encoding',
})
_base_response.status_code = 200


def current_bot_response(**defaults) -> Response:
    """
    Returns a mock of a bot calling itself by `@me`.

    Parameters
    ----------
    defaults:
        Values to be updated on the bot.
    """

    bot = {
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
    bot.update(defaults)

    response = copy.deepcopy(_base_response)
    response._content = json.dumps(bot).encode(encoding='utf-8')

    return response


def user_response(**defaults) -> Response:
    """
    Returns a mock of a Discord User response from API.

    Parameters
    ----------
    defaults:
        Values to be updated on the bot.
    """

    user = {
        'id': f'{fake.random_number(digits=18)}',
        'username': fake.user_name(),
        'avatar': fake.md5(),
        'avatar_decoration': None,
        'discriminator': ''.join([str(fake.pyint(min_value=1, max_value=9)) for _ in range(4)]),
        'public_flags': 1 << fake.pyint(min_value=0, max_value=19),
        'banner': fake.md5(),
        'banner_color': None,
        'accent_color': None
    }
    user.update(defaults)

    response = copy.deepcopy(_base_response)
    response._content = json.dumps(user).encode(encoding='utf-8')

    return response


def create_dm_response(**defaults) -> Response:
    """
    Response returned when creating a DM to a user.

    Parameters
    ----------
    defaults:
        Values to be updated on the bot.
    """

    user = user_response().json()
    dm = {
        'id': f'{fake.random_number(digits=18)}',
        'type': 1,  # Type 1 is DM
        'last_message_id': f'{fake.random_number(digits=18)}',
        'flags': 1 << fake.pyint(min_value=0, max_value=19),
        'recipients': [user],
    }
    dm.update(defaults)

    response = copy.deepcopy(_base_response)
    response._content = json.dumps(dm).encode(encoding='utf-8')

    return response


def create_dm_to_user_unavailable_response() -> Response:
    """
    Response returned whe creating a DM for a bot.
    """

    response = copy.deepcopy(_base_response)
    response.status_code = 400
    response._content = json.dumps({
        'message': 'Cannot send messages to this user',
        'code': 50007,
    }).encode(encoding='utf-8')

    return response
