import json

from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView


@method_decorator(staff_member_required(login_url='registration:auth:login'), name='dispatch')
class EmailView(TemplateView):
    """
    This view is intended to be used only on testing since it will be used to see how emails are being rendered.
    If you want to add context you should pass it as QueryParams.
    """

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
