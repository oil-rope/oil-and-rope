from django.core.paginator import InvalidPage
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView


class MultiplePaginatorListView(ListView):
    """
    Exact behaviour as :class:`ListView` except for the method :meth:`paginate_queryset_by_page_kwarg`.
    """

    def paginate_queryset_by_page_kwarg(self, queryset, page_size, page_kwarg):
        """
        Returns a queryset paginated by the `page_kwarg` argument as page number.
        """

        orphans = self.get_paginate_orphans()
        allow_empty = self.get_allow_empty()
        paginator = self.get_paginator(queryset, page_size, orphans, allow_empty)
        page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1

        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                raise Http404(_('Page is not “last”, nor can it be converted to an int.'))
        try:
            page = paginator.page(page_number)
            return paginator, page, page.object_list, page.has_other_pages()
        except InvalidPage as e:
            raise Http404(_('Invalid page (%(page_number)s): %(message)s') % {
                'page_number': page_number,
                'message': str(e)
            })
