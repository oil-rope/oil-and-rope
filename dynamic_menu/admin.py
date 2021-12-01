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
        'name_en',
        'name_es',
        'description',
        'description_en',
        'description_es',
        'prepended_text',
        'appended_text',
        'parent',
        'url_resolver',
        'extra_urls_args',
        'order',
        'staff_required',
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
    )
    raw_id_fields = ('permissions_required', )
    search_fields = ('name',)
