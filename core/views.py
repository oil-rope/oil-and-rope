from django.views.generic import RedirectView
from django.urls import reverse_lazy


class IndexView(RedirectView):
    """
    It just displays the index page.
    """

    url = reverse_lazy('registration:login')
