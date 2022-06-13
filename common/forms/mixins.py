from common.templatetags.string_utils import capfirstletter as cfl


class FormCapitalizeMixin:
    """
    Simple mixin to capitalize all labels and help texts.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.fields:
            raise AttributeError('Form has no fields defined.')
        for field in self.fields:
            self.fields[field].label = cfl(self.fields[field].label)
            self.fields[field].help_text = cfl(self.fields[field].help_text)
