# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Chat, ChatMessage


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    date_hierarchy = 'entry_created_at'
    list_display_links = ('id', 'name')
    list_display = (
        'name',
        'id',
        'entry_created_at',
        'entry_updated_at',
    )
    list_filter = ('entry_created_at', 'entry_updated_at')
    search_fields = (
        'name',
        'users__username',
    )


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    date_hierarchy = 'entry_created_at'
    list_display_links = (
        'id',
    )
    list_display = (
        'id',
        'chat',
        'author',
        'message',
        'entry_created_at',
        'entry_updated_at',
    )
    list_filter = (
        'entry_created_at',
        'entry_updated_at',
        'chat',
        'author'
    )
    search_fields = (
        'message',
        'author__username',
    )
