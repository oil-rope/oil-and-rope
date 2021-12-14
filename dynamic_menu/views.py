from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView

from common.views import StaffRequiredMixin

from . import forms, models


class DynamicMenuCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = models.DynamicMenu
    form_class = forms.DynamicMenuForm
    template_name = 'dynamic_menu/dynamic_menu/create.html'
