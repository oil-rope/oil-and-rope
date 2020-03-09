
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Field, Layout, Reset, Submit
from django import forms
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .models import Profile


class UpdateProfileForm(forms.ModelForm):
    """
    Formulario que gestiona la actualización de un usuario.
    """

    class Meta:
        model = Profile
        fields = ('bio', 'birthday', 'language', 'alias', 'laboral_category')
        widgets = {
            'birthday': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date'
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super(UpdateProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            # Imagen de perfil
            HTML(
                '{% if profile.images.all %} \
                <h5>Imagen</h5> \
                <img src="{{ profile.images.first.image.url }}" alt="Imagen de perfil" class="w-25vh img-thumbnail"> \
                {% endif %}'),
            # Botón para añadir imágenes
            HTML(
                '<div class="w-100 my-2"></div> \
                <a target="_blank" href="{% url \'registration:profile_image_update\' %}" class="btn btn-info"> \
                    Añadir imagen \
                </a>'
            ),
            Field('bio'),
            Field('birthday'),
            Field('language'),
            Field('alias'),
            Field('laboral_category'),
        )
        self.helper.add_input(Submit('submit', _('Update')))

    def clean_birthday(self):
        """
        La fecha de nacimiento no puede ser mayor que la fecha de hoy.
        """

        if self.cleaned_data['birthday']:
            data = self.cleaned_data['birthday']
            if data > timezone.datetime.today().date():
                raise forms.ValidationError(_('Birthday cannot be after today.'))
            return data


class UpdateProfileImageForm(forms.Form):
    """
    Formulario que gestiona las imágenes asociadas a un perfil.
    """

    def __init__(self, *args, **kwargs):
        super(UpdateProfileImageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('submit', _('Add')))
        self.helper.add_input(Reset('reset', _('Reset'), css_class='btn btn-secondary'))

    image = forms.ImageField(
        label='',
    )
