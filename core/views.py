from django.urls import reverse_lazy
from django.views.generic import RedirectView


class IndexView(RedirectView):
    """
    It just displays the index page.
    """

    url = reverse_lazy('registration:login')
