from typing import Optional, Type, cast

from crispy_forms.helper import FormHelper
from django import forms
from django.contrib import messages
from django.contrib.contenttypes.forms import BaseGenericInlineFormSet, generic_inlineformset_factory
from django.db import models
from django.http import HttpResponse

from common.forms import ImageForm
from common.models import Image
from core.types import HasFormMixinLogic, HasModelProtocol, HasObjectProtocol, HasRequestProtocol


class ImageFormsetMixin(HasRequestProtocol, HasModelProtocol, HasObjectProtocol, HasFormMixinLogic):
    """
    This mixin allows to manage the :class:`~common.models.Image` model for creating and associating images to another
    entry.

    Attributes
    ~~~~~~~~~~
    image_formset_prefix: :class`Optional[str]`
        Declare the prefix for all the forms in formset. If not set uses app label name and model name followed by
        'image'.
        For example for :class:`roleplay.models.Race` the prefix will be 'roleplay-race-image'.
    image_formset_template: :class:`str`
        Template used by :class:`crispy_forms.helper.FormHelper` to render the forms.
    image_formset_add_form_tag: :class:`bool`
        Declares if the `<form>` tag should be rendered. You might not want this to be rendered if this formset is
        inside another form.
    """

    image_formset_prefix: Optional[str] = None
    image_formset_template: str = 'bootstrap5/table_inline_formset.html'
    image_formset_add_form_tag: bool = False

    def get_image_formset_helper(self):
        helper = FormHelper()
        helper.template = self.image_formset_template
        helper.form_tag = self.image_formset_add_form_tag
        return helper

    def get_image_formset_factory_kwargs(self):
        kwargs = {
            'model': Image,
            'form': ImageForm,
            'ct_field': 'content_type',
            'fk_field': 'object_id',
            'extra': 3,
            'can_delete': False,
            'max_num': 3,
            'validate_max': True,
            'for_concrete_model': True,
        }
        return kwargs

    def get_image_formset_kwargs(self):
        kwargs = {
            'form_kwargs': {'owner': self.request.user},
            'prefix': self.get_image_formset_prefix(),
            'instance': self.object,
        }
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_image_formset_prefix(self) -> str:
        if self.image_formset_prefix:
            return self.image_formset_prefix
        return f'{self.model._meta.app_label}-{self.model._meta.model_name}-image'

    def get_image_formset(self):
        FormSet: Type[BaseGenericInlineFormSet] = generic_inlineformset_factory(
            **self.get_image_formset_factory_kwargs()
        )
        image_formset = FormSet(**self.get_image_formset_kwargs())
        return image_formset

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        if 'image_formset' not in kwargs:
            context_data['image_formset'] = self.get_image_formset()
        context_data['image_formset_helper'] = self.get_image_formset_helper()
        return context_data

    def form_invalid(
            self,
            form: forms.BaseModelForm,
            image_formset: Optional[BaseGenericInlineFormSet] = None,
    ) -> HttpResponse:
        if not image_formset:
            image_formset = self.get_image_formset()
        formset_non_form_errors = image_formset.non_form_errors()
        if formset_non_form_errors:
            for error in formset_non_form_errors:
                messages.error(self.request, error)
        return self.render_to_response(self.get_context_data(form=form, image_formset=image_formset))

    def form_valid(self, form: forms.BaseModelForm) -> HttpResponse:
        self.object = cast(models.Model, form.save(commit=False))
        image_formset = self.get_image_formset()
        if image_formset.is_valid():
            self.object.save()
            image_formset.save()
            return super().form_valid(form=form)
        else:
            return self.form_invalid(form=form, image_formset=image_formset)
