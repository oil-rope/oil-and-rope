from typing import Optional

from django import template
from django.db import models
from django.shortcuts import resolve_url
from django.template.defaultfilters import capfirst, stringfilter
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

    entries = [t.strip() for t in text.split(',')]
    values = {}
    for entry in entries:
        if '=' not in entry:
            values.update({entry: '#no-url'})
            continue
        breadcrumb, url = entry.split('=')
        try:
            url = resolve_url(url)
        except NoReverseMatch:
            url = '#no-url'
        values.update({breadcrumb: url})

    return values


@register.filter(is_safe=True)
@stringfilter
def capfirstletter(text: str):
    """
    Same behavior as `django.template.defaultfilters.capfirst` but only uppercase if is letter.
    """

    first_letter = 0
    for letter in text:
        if letter.isalpha():
            break
        first_letter += 1

    return text[:first_letter] + capfirst(text[first_letter:])


@register.filter
def verbose_name(object: models.Model, field: Optional[str] = None) -> str:
    """
    Using the given object it will return its verbose name. If `field` it's given then the verbose name returned will be
    for the field.
    """

    model: models.Model = object._meta.model
    if not field:
        return model._meta.verbose_name
    field = model._meta.get_field(field_name=field)
    return field.verbose_name


@register.filter
def verbose_name_plural(object: models.Model) -> str:
    """
    Given an object it will return its verbose name plural.
    """

    model: models.Model = object._meta.model
    return model._meta.verbose_name_plural
