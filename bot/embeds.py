from datetime import datetime
from typing import Optional

from django.utils import timezone
from pydantic import BaseModel, Field

from bot.enums import EmbedTypes


class Embed(BaseModel):
    """
    An Embed object for Discord.
    For more information see https://discord.com/developers/docs/resources/channel#embed-object.
    """

    title: Optional[str] = Field(default=None, max_length=256)
    type: Optional[EmbedTypes] = None
    description: Optional[str] = Field(default=None, max_length=4096)
    url: Optional[str] = None
    timestamp: Optional[datetime] = Field(default_factory=timezone.now)
    color: Optional[int] = None
    footer: Optional['EmbedFooter'] = None
    image: Optional['EmbedImage'] = None
    thumbnail: Optional['EmbedThumbnail'] = None
    video: Optional['EmbedVideo'] = None
    provider: Optional['EmbedProvider'] = None
    author: Optional['EmbedAuthor'] = None
    fields: Optional[list['EmbedField']] = None


class EmbedFooter(BaseModel):
    """
    Object that translate into Discord-like object EmbedFooter.
    For more information see https://discord.com/developers/docs/resources/channel#embed-object-embed-footer-structure.
    """

    text: str = Field(max_length=2048)
    icon_url: Optional[str] = None
    proxy_icon_url: Optional[str] = None


class EmbedImage(BaseModel):
    """
    An Embed Image object from Discord.
    For more information see https://discord.com/developers/docs/resources/channel#embed-object-embed-image-structure.
    """

    url: str
    proxy_url: Optional[str] = None
    height: Optional[int] = None
    width: Optional[int] = None


class EmbedThumbnail(BaseModel):
    """
    An Embed Thumbnail object from Discord.
    For more information see
    https://discord.com/developers/docs/resources/channel#embed-object-embed-thumbnail-structure.
    """

    url: str
    proxy_url: Optional[str] = None
    height: Optional[int] = None
    width: Optional[int] = None


class EmbedVideo(BaseModel):
    """
    An Embed Video object from Discord.
    For more information see https://discord.com/developers/docs/resources/channel#embed-object-embed-video-structure.
    """

    url: str
    proxy_url: Optional[str] = None
    height: Optional[int] = None
    width: Optional[int] = None


class EmbedProvider(BaseModel):
    """
    An Embed Provider object from Discord.
    For more information see
    https://discord.com/developers/docs/resources/channel#embed-object-embed-provider-structure.
    """

    name: Optional[str] = None
    url: Optional[str] = None


class EmbedAuthor(BaseModel):
    """
    An Embed Author object from Discord.
    For more information see https://discord.com/developers/docs/resources/channel#embed-object-embed-author-structure.
    """

    name: str = Field(max_length=256)
    url: Optional[str] = None
    icon_url: Optional[str] = None
    proxy_icon_url: Optional[str] = None


class EmbedField(BaseModel):
    """
    An Embed Field object from Discord.
    For more information see https://discord.com/developers/docs/resources/channel#embed-object-embed-field-structure.
    """

    name: str = Field(max_length=256)
    value: str = Field(max_length=1024)
    inline: Optional[bool] = None
