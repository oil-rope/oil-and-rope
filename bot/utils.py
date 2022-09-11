import json
import logging
from typing import Any, Optional

import requests
from django.conf import settings

from bot.enums import HttpMethods
from bot.exceptions import DiscordApiException

LOGGER = logging.getLogger(__name__)

NO_ERROR_STATUS = (200, 201, 202, 100, 101)


def discord_api_request(url: str, method: str = HttpMethods.GET, data: Optional[dict[str, Any]] = None):
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
    if method == HttpMethods.POST:
        response = requests.post(url, headers=headers, data=data)
    if method == HttpMethods.PATCH:
        response = requests.patch(url, headers=headers, data=data)

    if not response.ok:
        LOGGER.warning('%d | %s | %s', response.status_code, response.request.method, url)

    return response


def discord_api_post(url, data=None):
    """
    Makes a POST request to the give URL.
    """

    response = discord_api_request(url=url, method=HttpMethods.POST, data=data)

    if response.ok:
        return response

    raise DiscordApiException(response)


def discord_api_get(url):
    """
    Makes a GET request to the given URL.
    """

    response = discord_api_request(url=url, method=HttpMethods.GET)

    if response.ok:
        return response
    raise DiscordApiException(response)


def discord_api_patch(url, data=None):
    """
    Makes a PATCH request to the given URL.
    """

    response = discord_api_request(url=url, method=HttpMethods.PATCH, data=data)

    if response.ok:
        return response
    raise DiscordApiException(response)
