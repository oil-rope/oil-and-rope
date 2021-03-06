import json

import requests
from django.conf import settings

from ..exceptions import DiscordApiException
from .enums import HttpMethods

NO_ERROR_STATUS = (200, 201, 202, 100, 101)


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
    if method == HttpMethods.PATCH:
        response = requests.patch(url, headers=headers, data=data)
        return response


def discord_api_post(url, data=None):
    """
    Makes a POST request to the give URL.
    """

    response = discord_api_request(url=url, method=HttpMethods.POST, data=data)

    if response.status_code not in NO_ERROR_STATUS:
        raise DiscordApiException(response)

    return response


def discord_api_get(url):
    """
    Makes a GET request to the given URL.
    """

    response = discord_api_request(url=url, method=HttpMethods.GET)

    if response.status_code not in NO_ERROR_STATUS:
        raise DiscordApiException(response)

    return response


def discord_api_patch(url, data=None):
    """
    Makes a PATCH request to the given URL.
    """

    response = discord_api_request(url=url, method=HttpMethods.PATCH, data=data)

    if response.status_code not in NO_ERROR_STATUS:
        raise DiscordApiException(response)

    return response
