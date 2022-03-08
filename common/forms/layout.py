from crispy_forms import layout
from crispy_forms.utils import TEMPLATE_PACK, flatatt
from django.template.base import Template
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _


class SubmitClearLayout(layout.Layout):
    """
    Simple layout with :class:`layout.Submit` button and optional `layout.Reset` button.
    """

    def __init__(self, **kwargs):
        self.submit_text = kwargs.pop('submit_text', _('create').title())
        self.reset_button = kwargs.pop('reset_button', True)
        self.reset_text = kwargs.pop('reset_text', _('clear').title())
        self.reset_css_class = kwargs.pop('reset_css_class', '')
        self.submit_css_class = kwargs.pop('submit_css_class', '')
        self.buttons = (
            layout.Submit('create', self.submit_text, css_class=f'btn btn-primary col {self.submit_css_class}'),
        )

        if self.reset_button:
            self.buttons += (
                layout.Reset('reset', self.reset_text, css_class=f'btn btn-dark col {self.reset_css_class}'),
            )

        super().__init__(
            layout.Row(
                *self.buttons,
                css_class='justify-content-around',
            ),
        )


class Link(layout.LayoutObject):
    field_classes = "btn"
    template = '%s/layout/link.html'

    def __init__(self, content, url, new_tab=False, icon=None, **kwargs):
        self.content = content
        self.url = url
        self.new_tab = new_tab
        self.icon = icon
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
