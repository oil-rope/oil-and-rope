from core.forms import DateHTML5Field
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Field, Layout, Submit
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext
from django.utils.translation import ugettext_lazy as _

from .models import Profile


class SignUpForm(UserCreationForm):
    """
    Form that handles user creation.
    """

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class = 'col-12 col-lg-8 row justify-content-start'
        self.helper.form_id = 'registerForm'
        self.helper.layout = Layout(
            Field('username', wrapper_class='col-12 col-lg-6'),
            Field('email', wrapper_class='col-12 col-lg-6'),
            Field('password1', wrapper_class='col-6'),
            Field('password2', wrapper_class='col-6'),
            Field('first_name', wrapper_class='col-6'),
            Field('last_name', wrapper_class='col-6'),
            Field('birthday', wrapper_class='col-6 col-lg-4'),
            Field('language', wrapper_class='col-6 col-lg-4'),
            Field('avatar', wrapper_class='col-12 col-lg-4'),
            Field('terms_check', wrapper_class='col-12'),
            Div(
                Div(
                    HTML(
                        '<a class="btn-link" href="{% url \'core:home\' %}">' + gettext('Terms of Service') + '</a>' +
                        '<a class="btn-link" href="{% url \'core:home\' %}">' + gettext('Etiquettes') + '</a>'
                    ),
                    css_class='row justify-content-around'
                ),
                css_class='container-fluid pb-4'
            ),
            Submit('submit', _('Register'), css_class='btn text-uppercase btn-extra col-12')
        )

    first_name = forms.CharField(label=_('First name'), required=False)
    last_name = forms.CharField(label=_('Last name'), required=False)
    email = forms.EmailField(label=_('Email'), required=True)
    birthday = DateHTML5Field(label=_('Birthday'), required=False)
    language = forms.ChoiceField(label=_('Language'), choices=Profile.T_LANGUAGES, required=False)
    avatar = forms.FileField(label=_('Avatar'), required=False)
    terms_check = forms.BooleanField(label=_('I have read and agree with the Terms of Service & Etiquette.'),
                                     required=False)

    def clean_birthday(self):
        data = self.cleaned_data['birthday']
        if data and data > timezone.now().date():
            self.add_error('birthday', _('Birthday must be settled before today.'))
        return data

    def clean_email(self):
        data = self.cleaned_data["email"]
        if data and data in User.objects.values_list('email', flat=True):
            self.add_error('email', _('This email is already in use.'))
        return data

    def clean_terms_check(self):
        data = self.cleaned_data["terms_check"]
        if not data:
            self.add_error('terms_check', _('You must accept Terms of Service & Etiquette in order to continue.'))
        return data
