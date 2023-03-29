from typing import Any, OrderedDict

from common.templatetags.string_utils import capfirstletter as cfl


class FilterCapitalizeMixin:
    """
    Simple mixin to capitalize all labels and help texts.
    """

    filters: OrderedDict

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.filters:
            raise AttributeError('Form has no filters defined.')
        for filter_name in self.filters:
            self.filters[filter_name].label = cfl(self.filters[filter_name].label)
            if 'help_text' in self.filters[filter_name].extra:
                help_text = self.filters[filter_name].extra['help_text']
                self.filters[filter_name].extra['help_text'] = cfl(help_text)
            if 'choices' in self.filters[filter_name].extra:
                choices: list[tuple[Any, str]] = self.filters[filter_name].extra['choices']
                choices = [(v1, cfl(v2)) for v1, v2 in choices]
                self.filters[filter_name].extra['choices'] = choices
