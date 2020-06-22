import requests
import json
import enum
from django.conf import settings


class HttpMethods(enum.Enum):
    """
    Declares supported methods.
    """

    GET = 'GET'


def discord_api_request(url, method=HttpMethods.GET, data=None):
    """
    Makes a requests to the URL with the current Bot got from settings.
    """

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bot {settings.BOT_TOKEN}'
    }
    data = json.dumps(data) if data else json.dumps({})

    if method == HttpMethods.GET:
        response = requests.get(url, headers=headers, data=data)
        return response
