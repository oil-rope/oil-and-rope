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
    DOTS_HORIZONATL_TRIPLE = '<i class="ic-dots-horizontal-triple"></i>', _('dots horizontal triple')
    MENU_THIN = '<i class="ic-menu-thin"></i>', _('menu thin')
    CIRCLE_CROSS_THIN = '<i class="ic-circle-cross-thin"></i>', _('circle cross thin')
    CROSS_THIN = '<i class="ic-cross-thin"></i>', _('cross thin')
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
