from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import reverse
from django.views.generic import TemplateView

from . import models


class ChatView(LoginRequiredMixin, TemplateView):
    template_name = 'chat/index.html'

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        if not user.is_superuser:
            return HttpResponseForbidden()

        return super().dispatch(request, *args, **kwargs)

    def get_websocket_url(self):
        ws_url = 'ws://' if settings.DEBUG else 'wss://'
        ws_host = settings.WS_HOST
        if ws_host:
            ws_url += ws_host
        else:
            ws_url += self.request.get_host()
        ws_url += reverse('chat_ws:connect')

        return ws_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chat'] = models.Chat.objects.first()
        context['ws_url'] = self.get_websocket_url()

        return context
