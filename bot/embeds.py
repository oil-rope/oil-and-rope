import json

from django.utils import timezone

from bot.enums import EmbedTypes


class Embed:
    """
    An Embed object for Discord.

    Parameters
    ----------
    title: :class:`str`
        String	title of embed.
    type: :class:`EmbedTypes`
        Type of embed.
    description: :class:`str`
        String	description of embed.
    url: :class:`str`
        String	url of embed.
    timestamp: :clas:`datetime`
        ISO8601 timestamp timestamp of embed content.
    color: :class:`int`
        Integer	color code of the embed.
    """

    def __init__(self, title='', embed_type=EmbedTypes.RICH, description='', url='', timestamp=timezone.now(),
                 color=0, footer=None):
        self.title = title
        self.embed_type = embed_type
        self.description = description
        self.url = url
        self.timestamp = timestamp
        self.color = color
        self.footer = footer

    @property
    def data(self):
        """
        Transform this object into dictionary.
        """

        data = {
            'title': self.title,
            'type': self.embed_type.value,
            'description': self.description,
            'url': self.url,
            'timestamp': str(self.timestamp),
            'color': self.color
        }

        if self.footer:
            data['footer'] = self.footer.data

        return data

    def to_json(self):
        """
        Transform this object into a Discord-like embed object.
        """

        data = self.data
        return json.dumps(data)


class EmbedFooter:
    """
    Object that translate into Discor-like object EmbedFooter.

    Parameters
    ----------
    text: :class:`str`
        String footer text.
    icon_url: :class:`str`
        String url of footer icon (only supports http(s) and attachments).
    proxy_icon_url: :class:`str`
        String a proxied url of footer icon.
    """

    def __init__(self, text='', icon_url='', proxy_icon_url=''):
        self.text = text
        self.icon_url = icon_url
        self.proxy_icon_url = proxy_icon_url

    @property
    def data(self):
        """
        Transform this object into dictionary.
        """

        data = {
            'text': self.text,
            'icon_url': self.icon_url,
            'proxy_icon_url': self.proxy_icon_url,
        }

        return data

    def to_json(self):
        """
        Transform this object into a Discord-like embed object.
        """

        data = self.data
        return json.dumps(data)
