from django.views.generic import TemplateView

from . import models


class BaseChatView(TemplateView):
    template_name = 'chat/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chat'] = models.Chat.objects.first()
        return context
