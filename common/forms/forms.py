from crispy_forms.helper import FormHelper
from django import forms

from common.models import Image
from registration.models import User

from .mixins import FormCapitalizeMixin


class ImageForm(FormCapitalizeMixin, forms.ModelForm):
    """
    This form is intended to be used alongside with `:class:~django.contrib.contenttypes.forms.BaseGenericInlineFormSet`
    so the owner of the image will always be the user creating the instance that requires images.

    Parameters
    ----------
    owner: `:class:~registration.models.User`
        The user owner of this image.
    """

    def __init__(self, owner: User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.owner = owner

        self.helper = FormHelper(self)
        self.helper.form_tag = False

    class Meta:
        fields = ('image', )
        model = Image

    def save(self, commit=True):
        self.instance.owner = self.owner
        return super().save(commit=commit)
