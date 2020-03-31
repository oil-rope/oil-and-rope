import random

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class SheetHeader(models.Model):
    """
    Sheet

    Parameters
    ----------
    name: class:`str`
    game: :class:`Game`
    character_info: class:`CharacterInfo`
    user: :class:`User`
    """

    name = models.CharField(verbose_name=_("Name"), max_length=50)
    # Game

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), on_delete=models.CASCADE)
    character_info = models.OneToOneField("sheet.CharacterInfo", verbose_name=_("Character Info"),
                                          on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Sheet Header")
        verbose_name_plural = _("Sheet Headers")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("sheetheader_detail", kwargs={"pk": self.pk})


class CharacterInfo(models.Model):
    """
    The character info depends of the game. At the moment, is tatic, but due to be changed when i have a better idea
    of how to to it

    parameters
    ----------
    name: :class:`str`
    age: :class:`int`
    height: :class:`float`
        This should be either in m or ft.
    weight: :class:`float`
    hair_color: :class:`str`
    eye_color: :class:`str`
    height_measurement_system: :class:`select`
    weight_measurement_system: :class:`select`
    """

    name = models.CharField(verbose_name=_("Name"), max_length=50)
    age = models.IntegerField(verbose_name=_("Age"))
    height = models.DecimalField(verbose_name=_("Height"), max_digits=5, decimal_places=2, null=True, blank=True)
    weight = models.DecimalField(verbose_name=_("Weight"), max_digits=5, decimal_places=2, null=True, blank=True)
    hair_color = models.CharField(verbose_name=_("Hair Color"), max_length=30, null=True, blank=True)
    eye_color = models.CharField(verbose_name=_("Eye Color"), max_length=30, null=True, blank=True)

    METRIC = 0
    US = 1
    MEASUREMENT_SYSTEM = (
        (METRIC, _('Metric')),
        (US, _('US Standard')),
    )

    height_measurement_system = models.PositiveSmallIntegerField(verbose_name=_("Height Measurement System"),
                                                                 choices=MEASUREMENT_SYSTEM, default=0)
    WEIGHT_MEASUREMENT_SYSTEM = models.PositiveSmallIntegerField(verbose_name=_("Weight Measurement System"),
                                                                 choices=MEASUREMENT_SYSTEM, default=0)

    class Meta:
        verbose_name = _("Character Info")
        verbose_name_plural = _("Character Infos")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("CharacterInfo_detail", kwargs={"pk": self.pk})


class SheetDetail(models.Model):
    """
    In this model all the attribute skills and rolls are described.

    Parameters
    ----------
    name: :class:`str`
    start_value: :class:`int`
        Ex: the start value of str is 10 in pathfinder, but 0
    rollable: :class:`bool`
    dice_class: :class:`int`
    dice_number: :class:`int`
    inherited_bonus: :class:`SheetDetail`
        In this case, we'll take the bonus of another detail (example: perception uses wisdom)
    misc_bonus: :class:`int`
    extra_bonus_1: :class:`int`
    extra_bonus_2: :class:`int`
    sheet: :class:`Sheet`
    """

    name = models.CharField(verbose_name=_("Name"), max_length=50)
    start_value = models.SmallIntegerField(verbose_name=_("Start Value"), default=0)
    rollable = models.BooleanField(verbose_name=_("Rollable"), default=True)

    D3 = 0
    D4 = 1
    D6 = 2
    D8 = 3
    D10 = 4
    D12 = 5
    D16 = 6
    D20 = 7
    D100 = 8

    DICES = (
        (D3, _("D3")),
        (D4, _("D4")),
        (D6, _("D6")),
        (D8, _("D8")),
        (D10, _("D10")),
        (D12, _("D12")),
        (D16, _("D16")),
        (D20, _("D20")),
        (D100, _("D100")),
    )

    dice_class = models.PositiveSmallIntegerField(verbose_name=_("Dice Class"), default=20)
    dice_number = models.PositiveSmallIntegerField(verbose_name=_("Dice Number"), default=1)
    # Inherited bonus
    misc_bonus = models.SmallIntegerField(verbose_name=_("Miscelaneous Bonus"), default=0)
    extra_bonus_1 = models.SmallIntegerField(verbose_name=_("Extra Bonus 1"), default=0)
    extra_bonus_2 = models.SmallIntegerField(verbose_name=_("Extra Bonus 2"), default=0)
    sheet = models.ForeignKey("sheet.SheetHeader", verbose_name=_("Sheet Header"),
                              on_delete=models.CASCADE, related_name="sheet_details")

    @property
    def get_total_bonus(self):
        return self.misc_bonus + self.extra_bonus_1 + self.extra_bonus_2

    @property
    def roll(self):

        if self.rollable:

            random.seed()
            roll = self.start_value

            for i in range(self.dice_number):
                roll += random.randrange(1, self.dice_class)

            roll = roll + self.get_total_bonus

            return roll

        else:
            value = self.start_value + self.get_total_bonus
            return value

    class Meta:
        verbose_name = _("Sheet Detail")
        verbose_name_plural = _("Sheet Details")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("sheetdetail_detail", kwargs={"pk": self.pk})
