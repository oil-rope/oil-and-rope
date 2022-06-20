import enum

from django.db import models
from django.utils.translation import gettext_lazy as _


class AvailableIcons(models.TextChoices):
    """
    A list of available Icons for the web.
    """

    JOIN = '<i class="ic-join"></i>', _('join')
    CONNECT = '<i class="ic-connect"></i>', _('connect')
    ARROW_RIGHT = '<i class="ic-arrow-right"></i>', _('arrow right')
    ARROW_LEFT = '<i class="ic-arrow-left"></i>', _('arrow left')
    ARROW_UP = '<i class="ic-arrow-up"></i>', _('arrow up')
    LOOP = '<i class="ic-loop"></i>', _('loop')
    REDO = '<i class="ic-redo"></i>', _('redo')
    UNDO = '<i class="ic-undo"></i>', _('undo')
    FACEBOOK = '<i class="ic-facebook"></i>', 'Facebook'
    MAIL = '<i class="ic-mail"></i>', _('mail')
    SHARE = '<i class="ic-share"></i>', _('share')
    MENU = '<i class="ic-menu"></i>', _('menu')
    DICE = '<i class="ic-dice"></i>', _('dice')
    USER_CHECK = '<i class="ic-user-check"></i>', _('user check')
    USER = '<i class="ic-user"></i>', _('user')
    USERS = '<i class="ic-users"></i>', _('users')
    SHIELD = '<i class="ic-shield"></i>', _('shield')
    HAMMER = '<i class="ic-hammer"></i>', _('hammer')
    ARROW_DOWN = '<i class="ic-arrow-down"></i>', _('arrow down')
    COG = '<i class="ic-cog"></i>', _('cog')
    COGS = '<i class="ic-cogs"></i>', _('cogs')
    CROSS = '<i class="ic-cross"></i>', _('cross')
    TRASH = '<i class="ic-trash"></i>', _('trash')
    TOWN = '<i class="ic-town"></i>', _('town')
    HOME = '<i class="ic-home"></i>', _('home')
    CITY = '<i class="ic-city"></i>', _('city')
    EDIT = '<i class="ic-edit"></i>', _('edit')
    PENCIL = '<i class="ic-pencil"></i>', _('pencil')
    QUILL = '<i class="ic-quill"></i>', _('quill')
    MAP = '<i class="ic-map"></i>', _('map')
    WORLD = '<i class="ic-world"></i>', _('world')
    FLAG = '<i class="ic-flag"></i>', _('flag')
    PLUS = '<i class="ic-plus"></i>', _('plus')
    MINUS = '<i class="ic-minus"></i>', _('minus')
    TV = '<i class="ic-tv"></i>', 'TV'
    EYE = '<i class="ic-eye"></i>', _('eye')
    RESPONSIVE_DEVICE = '<i class="ic-responsive-device"></i>', _('responsive device')
    TRIANGLE_RELATION = '<i class="ic-triangle-relation"></i>', _('triangle relation')
    DIANA = '<i class="ic-diana"></i>', _('diana')
    GLOBE = '<i class="ic-globe"></i>', _('globe')
    DOTS_HORIZONTAL_TRIPLE = '<i class="ic-dots-horizontal-triple"></i>', _('dots horizontal triple')
    MENU_THIN = '<i class="ic-menu-thin"></i>', _('menu thin')
    CIRCLE_CROSS_THIN = '<i class="ic-circle-cross-thin"></i>', _('circle cross thin')
    CROSS_THIN = '<i class="ic-cross-thin"></i>', _('cross thin')
    TWITTER = '<i class="ic-twitter"></i>', 'Twitter'
    GITHUB = '<i class="ic-github"></i>', 'GitHub'
    DISCORD = '<i class="ic-discord"></i>', 'Discord'
    GOOGLE = '<i class="ic-google"></i>', 'Google'
    SEARCH = '<i class="bi bi-search"></i>', _('search')
    THUMBS_UP = '<i class="bi bi-hand-thumbs-up"></i>', _('thumbs up')
    THUMBS_UP_FILL = '<i class="bi bi-hand-thumbs-up-fill"></i>', _('thumbs up fill')
    THUMBS_DOWN = '<i class="bi bi-hand-thumbs-down"></i>', _('thumbs down')
    THUMBS_DOWN_FILL = '<i class="bi bi-hand-thumbs-down-fill"></i>', _('thumbs down fill')
    INFO = '<i class="bi bi-info"></i>', _('info')
    INFO_LG = '<i class="bi bi-info-lg"></i>', _('info lg')
    CODE_SLASH = '<i class="bi bi-code-slash"></i>', _('code slash')
    FILE_EARMARK_CODE = '<i class="bi bi-file-earmark-code"></i>', _('file earmark code')

    @classmethod
    def choices_with_empty(cls):
        """
        Adds an empty value to the given choices.
        """

        choices = cls.choices
        choices.insert(0, ('', '-----'))
        return choices


class JavaScriptActions(enum.Enum):
    """
    List of JavaScript actions declared on `common/js/utils.js` or any other JavaScript file.
    """

    GO_BACK = 'window.history.back();'


class WebSocketCloseCodes(enum.Enum):
    """
    List of WebSocket close codes.
    """

    NORMAL_CLOSURE = 1000
    GOING_AWAY = 1001
    PROTOCOL_ERROR = 1002
    UNSUPPORTED_DATA = 1003
    RESERVED = 1004
    NO_STATUS_RCVD = 1005
    ABNORMAL_CLOSURE = 1006
    INVALID_FRAME_PAYLOAD_DATA = 1007
    POLICY_VIOLATION = 1008
    MESSAGE_TOO_BIG = 1009
    MANDATORY_EXT = 1010
    INTERNAL_ERROR = 1011
    SERVICE_RESTART = 1012
    TRY_AGAIN_LATER = 1013
    TLS_HANDSHAKE = 1015
    UNAUTHORIZED = 3000
