from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView

from common.templatetags.string_utils import capfirstletter as cfl
from common.views import StaffRequiredMixin

from . import forms, models


class DynamicMenuCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = models.DynamicMenu
    form_class = forms.DynamicMenuForm
    template_name = 'dynamic_menu/dynamic_menu/create.html'

    def form_valid(self, form):
        msg = cfl(_('menu created!'))
        messages.success(self.request, msg)
        return super().form_valid(form)
