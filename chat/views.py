from django.views.generic import TemplateView


class BaseChatView(TemplateView):
    template_name = 'chat/index.html'
