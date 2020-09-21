from django.db import models
from django.utils.translation import gettext_lazy as _


class AvailableIcons(models.TextChoices):
    """
    A list of available Icons for the web.
    """

    JOIN = '<i class="ic-join"></i>', _('Join')
    CONNECT = '<i class="ic-connect"></i>', _('Connect')
    ARROW_RIGHT = '<i class="ic-arrow-right"></i>', _('Arrow right')
    ARROW_LEFT = '<i class="ic-arrow-left"></i>', _('Arrow left')
    ARROW_UP = '<i class="ic-arrow-up"></i>', _('Arrow up')
    LOOP = '<i class="ic-loop"></i>', _('Loop')
    REDO = '<i class="ic-redo"></i>', _('Redo')
    UNDO = '<i class="ic-undo"></i>', _('Undo')
    FACEBOOK = '<i class="ic-facebook"></i>', _('Facebook')
    MAIL = '<i class="ic-mail"></i>', _('Mail')
    SHARE = '<i class="ic-share"></i>', _('Share')
    MENU = '<i class="ic-menu"></i>', _('Menu')
    DICE = '<i class="ic-dice"></i>', _('Dice')
    USER_CHECK = '<i class="ic-user-check"></i>', _('User Check')
    USER = '<i class="ic-user"></i>', _('User')
    USERS = '<i class="ic-users"></i>', _('Users')
    SHIELD = '<i class="ic-shield"></i>', _('Shield')
    HAMMER = '<i class="ic-hammer"></i>', _('Hammer')
    ARROW_DOWN = '<i class="ic-arrow-down"></i>', _('Arrow down')
    COG = '<i class="ic-cog"></i>', _('Cog')
    COGS = '<i class="ic-cogs"></i>', _('Cogs')
    CROSS = '<i class="ic-cross"></i>', _('Cross')
    TRASH = '<i class="ic-trash"></i>', _('Trash')
    TOWN = '<i class="ic-town"></i>', _('Town')
    HOME = '<i class="ic-home"></i>', _('Home')
    CITY = '<i class="ic-city"></i>', _('City')
    EDIT = '<i class="ic-edit"></i>', _('Edit')
    PENCIL = '<i class="ic-pencil"></i>', _('Pencil')
    QUILL = '<i class="ic-quill"></i>', _('Quill')
    MAP = '<i class="ic-map"></i>', _('Map')
    WORLD = '<i class="ic-world"></i>', _('World')
    FLAG = '<i class="ic-flag"></i>', _('Flag')
    PLUS = '<i class="ic-plus"></i>', _('Plus')
    MINUS = '<i class="ic-minus"></i>', _('Minus')
    TV = '<i class="ic-tv"></i>', _('TV')
    EYE = '<i class="ic-eye"></i>', _('Eye')
    RESPONSIVE_DEVICE = '<i class="ic-responsive-device"></i>', _('Responsive device')
    TRIANGLE_RELATION = '<i class="ic-triangle-relation"></i>', _('Triangle relation')
    DIANA = '<i class="ic-diana"></i>', _('Diana')
    GLOBE = '<i class="ic-globe"></i>', _('Globe')
    DOTS_HORIZONATL_TRIPLE = '<i class="ic-dots-horizontal-triple"></i>', _('Dots horizontal triple')
    MENU_THIN = '<i class="ic-menu-thin"></i>', _('Menu thin')
    CIRCLE_CROSS_THIN = '<i class="ic-circle-cross-thin"></i>', _('Circle cross thin')
    CROSS_THIN = '<i class="ic-cross-thin"></i>', _('Cross thin')
    TWITTER = '<i class="ic-twitter"></i>', _('Twitter')
    GITHUB = '<i class="ic-github"></i>', _('GitHub')
    DISCORD = '<i class="ic-discord"></i>', _('Discord')

    @classmethod
    def choices_with_empty(cls):
        """
        Adds an empty value to the given choices.
        """

        choices = cls.choices
        choices.insert(0, ('', '-----'))
        return choices
