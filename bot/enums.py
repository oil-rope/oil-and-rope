import enum


class HttpMethods(enum.Enum):
    """
    Declares supported methods.
    """

    GET = 'GET'
    POST = 'POST'
    PATCH = 'PATCH'


class ChannelTypes(enum.IntEnum):
    """
    List of channels supportes by Discord.

    Attributes
    ----------
    GUILD_TEXT:
        A text channel within a server.
    DM:
        A direct message between users.
    GUILD_VOICE:
        A voice channel within a server.
    GROUP_DM:
        A direct message between multiple users.
    GUILD_CATEGORY:
        An organizational category that contains up to 50 channels.
    GUILD_NEWS:
        A channel that users can follow and crosspost into their own server.
    GUILD_STORE:
        A channel in which game developers can sell their game on Discord.
    """

    GUILD_TEXT = 0
    DM = 1
    GUILD_VOICE = 2
    GROUP_DM = 3
    GUILD_CATEGORY = 4
    GUILD_NEWS = 5
    GUILD_STORE = 6


class MessageTypes(enum.IntEnum):

    DEFAULT = 0
    RECIPIENT_ADD = 1
    RECIPIENT_REMOVE = 2
    CALL = 3
    CHANNEL_NAME_CHANGE = 4
    CHANNEL_ICON_CHANGE = 5
    CHANNEL_PINNED_MESSAGE = 6
    GUILD_MEMBER_JOIN = 7
    USER_PREMIUM_GUILD_SUBSCRIPTION = 8
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_1 = 9
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_2 = 10
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_3 = 11
    CHANNEL_FOLLOW_ADD = 12
    GUILD_DISCOVERY_DISQUALIFIED = 14
    GUILD_DISCOVERY_REQUALIFIED = 15


class EmbedTypes(enum.Enum):
    """
    Supported types:
    ----------------
    rich:
        Generic embed rendered from embed attributes.
    image:
        Image embed.
    video:
        Video embed.
    gifv:
        Animated gif image embed rendered as a video embed.
    article:
        Article embed.
    link:
        Link embed.
    """

    RICH = 'rich'
    IMAGE = 'image'
    VIDEO = 'video'
    GIF = 'gifv'
    ARTICLE = 'article'
    LINK = 'link'
