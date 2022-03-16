import enum

from django.db import models
from django.utils.translation import gettext_lazy as _


class AvailableIcons(models.TextChoices):
    """
    A list of available Icons for the web.
    """

    JOIN = '<i class="ic-join"></i>', _('join').title()
    CONNECT = '<i class="ic-connect"></i>', _('connect').title()
    ARROW_RIGHT = '<i class="ic-arrow-right"></i>', _('arrow right').title()
    ARROW_LEFT = '<i class="ic-arrow-left"></i>', _('arrow left').title()
    ARROW_UP = '<i class="ic-arrow-up"></i>', _('arrow up').title()
    LOOP = '<i class="ic-loop"></i>', _('loop').title()
    REDO = '<i class="ic-redo"></i>', _('redo').title()
    UNDO = '<i class="ic-undo"></i>', _('undo').title()
    FACEBOOK = '<i class="ic-facebook"></i>', 'Facebook'
    MAIL = '<i class="ic-mail"></i>', _('mail').title()
    SHARE = '<i class="ic-share"></i>', _('share').title()
    MENU = '<i class="ic-menu"></i>', _('menu').title()
    DICE = '<i class="ic-dice"></i>', _('dice').title()
    USER_CHECK = '<i class="ic-user-check"></i>', _('user check').title()
    USER = '<i class="ic-user"></i>', _('user').title()
    USERS = '<i class="ic-users"></i>', _('users').title()
    SHIELD = '<i class="ic-shield"></i>', _('shield').title()
    HAMMER = '<i class="ic-hammer"></i>', _('hammer').title()
    ARROW_DOWN = '<i class="ic-arrow-down"></i>', _('arrow down').title()
    COG = '<i class="ic-cog"></i>', _('cog').title()
    COGS = '<i class="ic-cogs"></i>', _('cogs').title()
    CROSS = '<i class="ic-cross"></i>', _('cross').title()
    TRASH = '<i class="ic-trash"></i>', _('trash').title()
    TOWN = '<i class="ic-town"></i>', _('town').title()
    HOME = '<i class="ic-home"></i>', _('home').title()
    CITY = '<i class="ic-city"></i>', _('city').title()
    EDIT = '<i class="ic-edit"></i>', _('edit').title()
    PENCIL = '<i class="ic-pencil"></i>', _('pencil').title()
    QUILL = '<i class="ic-quill"></i>', _('quill').title()
    MAP = '<i class="ic-map"></i>', _('map').title()
    WORLD = '<i class="ic-world"></i>', _('world').title()
    FLAG = '<i class="ic-flag"></i>', _('flag').title()
    PLUS = '<i class="ic-plus"></i>', _('plus').title()
    MINUS = '<i class="ic-minus"></i>', _('minus').title()
    TV = '<i class="ic-tv"></i>', 'TV'
    EYE = '<i class="ic-eye"></i>', _('eye').title()
    RESPONSIVE_DEVICE = '<i class="ic-responsive-device"></i>', _('responsive device').title()
    TRIANGLE_RELATION = '<i class="ic-triangle-relation"></i>', _('triangle relation').title()
    DIANA = '<i class="ic-diana"></i>', _('diana').title()
    GLOBE = '<i class="ic-globe"></i>', _('globe').title()
    DOTS_HORIZONATL_TRIPLE = '<i class="ic-dots-horizontal-triple"></i>', _('dots horizontal triple').title()
    MENU_THIN = '<i class="ic-menu-thin"></i>', _('menu thin').title()
    CIRCLE_CROSS_THIN = '<i class="ic-circle-cross-thin"></i>', _('circle cross thin').title()
    CROSS_THIN = '<i class="ic-cross-thin"></i>', _('cross thin').title()
    TWITTER = '<i class="ic-twitter"></i>', 'Twitter'
    GITHUB = '<i class="ic-github"></i>', 'GitHub'
    DISCORD = '<i class="ic-discord"></i>', 'Discord'

    @classmethod
    def choices_with_empty(cls):
        """
        Adds an empty value to the given choices.
        """

        choices = cls.choices
        choices.insert(0, ('', '-----'))
        return choices


class JavaScriptAction(enum.Enum):
    """
    List of JavaScript actions declared on `common/js/utils.js` or any other JavaScript file.
    """

    GO_BACK = 'window.history.back();'
