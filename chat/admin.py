# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Chat, ChatMessage


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    raw_id_fields = ('users',)
    search_fields = ('name',)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'message', 'user', 'created_at')
    list_filter = ('chat', 'user', 'created_at')
    date_hierarchy = 'created_at'
