from django import template
from django.shortcuts import reverse
from django.template.defaultfilters import stringfilter
from django.urls.exceptions import NoReverseMatch

register = template.Library()


@register.filter
@stringfilter
def startswith(text, compare):
    return text.startswith(compare)


@register.filter
@stringfilter
def generate_breadcrumbs(text):
    """
    It expects a string with format `name=url, name=url, ...' and it will automatically convert that into a list of
    dictionaries `[{name: url}, {name: url}, ...]`.
    """

    entries = text.split(',')
    values = {}
    for entry in entries:
        entry = entry.split('=')
        breadcrumb = entry[0]
        try:
            url = entry[1]
            url = reverse(url)
        except (NoReverseMatch, IndexError):
            url = '#no-url'
        values.update({breadcrumb: url})

    return values
