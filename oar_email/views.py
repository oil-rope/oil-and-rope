import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView


class EmailView(LoginRequiredMixin, TemplateView):
    """
    This view is intended to be used only on testing since it will be used to see how emails are being rendered.
    If you want to add context you should pass it as QueryParams.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        if not request.user.is_staff:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        given_template = self.kwargs['mail_template']
        self.template_name = f'email_templates/{given_template}'
        return super().get_template_names()

    def parse_context(self):
        qp_context = self.request.GET.dict()
        for key, value in qp_context.items():
            if '{' in value or '}' in value:
                qp_context[key] = json.loads(value)
        return qp_context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'protocol': self.request.scheme, 'domain': self.request.headers.get('Host', 'localhost')})
        context.update(self.parse_context())
        return context
