from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView

from common.views import StaffRequiredMixin

from . import forms, models


class DynamicMenuCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = models.DynamicMenu
    form_class = forms.DynamicMenuForm
    template_name = 'dynamic_menu/dynamic_menu/create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context['form']
        context['name_container_display_id'] = form.display_name_container_id
        context['display_url_resolver_id'] = form.display_url_resolver_id
        return context
