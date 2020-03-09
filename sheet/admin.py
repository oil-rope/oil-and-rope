# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import CharacterInfo, SheetDetail, SheetHeader


@admin.register(SheetHeader)
class SheetHeaderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'character_info')
    list_filter = ('user', 'character_info')
    search_fields = ('name',)


@admin.register(CharacterInfo)
class CharacterInfoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'age',
        'height',
        'weight',
        'hair_color',
        'eye_color',
        'height_measurement_system',
        'WEIGHT_MEASUREMENT_SYSTEM',
    )
    search_fields = ('name',)


@admin.register(SheetDetail)
class SheetDetailAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'start_value',
        'rollable',
        'dice_class',
        'dice_number',
        'misc_bonus',
        'extra_bonus_1',
        'extra_bonus_2',
        'sheet',
    )
    list_filter = ('rollable', 'sheet')
    search_fields = ('name',)
