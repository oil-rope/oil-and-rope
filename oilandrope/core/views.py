from django.shortcuts import redirect, reverse
from django.views.generic import TemplateView


def index(request):
    return redirect(reverse('login'))


class IndexView(TemplateView):
    """
    It just displays the index page.
    """

    template_name = 'registration/login.html'
