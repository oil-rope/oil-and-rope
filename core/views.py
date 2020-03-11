from django.views.generic import TemplateView


class IndexView(TemplateView):
    """
    It just displays the index page.
    """

    template_name = 'core/index.html'
