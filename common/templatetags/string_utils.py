from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def startswith(text, compare):
    return text.startswith(compare)
