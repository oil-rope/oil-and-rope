from crispy_forms import layout
from crispy_forms.utils import TEMPLATE_PACK, flatatt
from django.template.base import Template
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _


class CreateClearLayout(layout.Layout):
    def __init__(self, reset_text=_('clear'), create_text=_('create')):
        super().__init__(
            layout.Row(
                layout.Reset('reset', reset_text.title(), css_class='btn btn-secondary col-5'),
                layout.Submit('create', create_text.title(), css_class='btn btn-primary col-5'),
                css_class='justify-content-around',
            ),
        )


class Link(layout.LayoutObject):
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
