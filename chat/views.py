from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import reverse
from django.views.generic import TemplateView

from . import models


class ChatView(LoginRequiredMixin, TemplateView):
    template_name = 'chat/index.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        return HttpResponseForbidden()

    def get_websocket_url(self):
        ws_url = 'ws://' if settings.DEBUG else 'wss://'
        ws_url += settings.WS_HOST + reverse('chat_ws:connect')
        return ws_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chat'] = models.Chat.objects.first()
        context['ws_url'] = self.get_websocket_url()
        return context
