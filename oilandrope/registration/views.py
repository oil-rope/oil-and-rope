from django.urls import reverse_lazy
from django.views.generic import CreateView
from oilandrope.settings import LANGUAGE_CODE

from .forms import SignUpForm


class SignUpView(CreateView):
    """
    View that handles the creation for a :class:`User`.
    """

    form_class = SignUpForm
    success_url = reverse_lazy('login')
    template_name = 'registration/register.html'

    def form_valid(self, form):
        response = super(SignUpView, self).form_valid(form)
        data = form.cleaned_data
        user = self.object
        user.email = data.get('email', '')
        user.first_name = data.get('first_name', '')
        user.last_name = data.get('last_name', '')
        user.save()
        profile = user.profile
        profile.birthday = data.get('birthday', None)
        profile.language = data.get('language', LANGUAGE_CODE)
        profile.image = data.get('avatar', None)
        profile.save()
        return response
