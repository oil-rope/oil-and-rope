from crispy_forms.layout import LayoutObject
from crispy_forms.utils import TEMPLATE_PACK, flatatt
from django.template.base import Template
from django.template.loader import render_to_string


class Link(LayoutObject):
    field_classes = "btn"
    template = '%s/layout/link.html'

    def __init__(self, content, url, **kwargs):
        self.content = content
        self.url = url
        self.template = kwargs.pop("template", self.template)

        # We turn  css_class into class
        kwargs["class"] = self.field_classes
        if "css_class" in kwargs:
            kwargs["class"] += " %s" % kwargs.pop("css_class")

        self.flat_attrs = flatatt(kwargs)

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs):
        self.content = Template(str(self.content)).render(context)
        template = self.get_template_name(template_pack)
        context.update({"link": self})

        return render_to_string(template, context.flatten())
