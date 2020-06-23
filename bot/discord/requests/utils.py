import enum
import json

import requests
from django.conf import settings

from ...exceptions import DiscordApiException


class HttpMethods(enum.Enum):
    """
    Declares supported methods.
    """

    GET = 'GET'
    POST = 'POST'


def discord_api_request(url, method=HttpMethods.GET, data=None):
    """
    Makes a request to the URL with the current Bot got from settings.
    """

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bot {settings.BOT_TOKEN}'
    }
    if data:
        data = json.dumps(data)

    if method == HttpMethods.GET:
        response = requests.get(url, headers=headers, data=data)
        return response
    if method == HttpMethods.POST:
        response = requests.post(url, headers=headers, data=data)
        return response


def discord_api_post(url, data=None):
    """
    Makes a POST request to the give URL.
    """

    response = discord_api_request(url=url, method=HttpMethods.POST, data=data)

    if response.status_code != 200:
        raise DiscordApiException(response)

    return response


def discord_api_get(url, data=None):
    """
    Makes a GET rquest to the given URL.
    """

    response = discord_api_request(url=url, method=HttpMethods.GET, data=data)

    if response.status_code != 200:
        raise DiscordApiException(response)

    return response
