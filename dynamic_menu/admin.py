# -*- coding: utf-8 -*-
from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import DynamicMenu


@admin.register(DynamicMenu)
class DynamicMenuAdmin(TranslationAdmin):
    list_display = (
        'id',
        'entry_created_at',
        'entry_updated_at',
        'name',
        'name_en_us',
        'name_es_ES',
        'description',
        'description_en_us',
        'description_es_ES',
        'prepended_text',
        'appended_text',
        'parent',
        'url_resolver',
        'extra_urls_args',
        'order',
        'staff_required',
        'superuser_required',
        'icon',
        'menu_type',
        'lft',
        'rght',
        'tree_id',
        'level',
    )
    list_filter = (
        'entry_created_at',
        'entry_updated_at',
        'parent',
        'staff_required',
        'superuser_required',
    )
    raw_id_fields = ('permissions_required', 'related_models')
    search_fields = ('name',)
