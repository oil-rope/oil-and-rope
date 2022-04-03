from crispy_forms import bootstrap, layout
from django.utils.translation import gettext_lazy as _

from common.enums import JavaScriptActions
from common.forms import layout as common_layout
from common.templatetags.string_utils import capfirstletter as cfl


class PlaceLayout(layout.Layout):
    def __init__(self, submit_text=_('create')):
        super().__init__(
            layout.Row(
                layout.Column(
                    'parent_site',
                    css_class='col-sm-12 col-lg-10'
                ),
                css_class='justify-content-lg-around',
            ),
            layout.Row(
                layout.Column(
                    'name',
                    css_class='col-sm-12 col-lg-10',
                ),
                layout.Column(
                    layout.Field('description', style='resize: none'),
                    css_class='col-sm-12 col-lg-10',
                ),
                css_class='justify-content-lg-around',
            ),
            layout.Row(
                layout.Column(
                    'site_type',
                    css_class='col-sm-6 col-md-10'
                ),
                layout.Column(
                    'image',
                    css_class='col-sm-6 col-md-10'
                ),
                css_class='justify-content-md-around',
            ),
            layout.Row(
                layout.Column(
                    common_layout.SubmitClearLayout(
                        submit_text=submit_text.capitalize(),
                        submit_css_class='col-5 col-lg-6',
                        reset_css_class='col-5 d-lg-none',
                    ),
                ),
            ),
            layout.Row(
                common_layout.Button(
                    content=_('go back').capitalize(),
                    css_class='btn-dark col-11 col-md-7 col-lg-6',
                    action=JavaScriptActions.GO_BACK.value,
                    icon='ic-arrow-left',
                ),
                css_class='justify-content-around mt-3 mt-md-5 mt-lg-3',
            ),
        )


class WorldFormLayout(layout.Layout):
    def __init__(self, submit_text):
        super().__init__(
            layout.Row(
                layout.Column(
                    layout.Field('name', placeholder='Middle-Earth, Narnia, Argos...'),
                    css_class='col-12 col-lg-7'
                ),
                layout.Column(
                    layout.Field(
                        'description',
                        placeholder=_(
                            'write something about your world, its civilizations, its culture...'
                        ).capitalize(),
                        style='resize: none',
                    ),
                    css_class='col-12 col-lg-7'
                ),
                layout.Column(
                    layout.Field('image'),
                    css_class='col-12 col-lg-7'
                ),
                css_class='justify-content-lg-around'
            ),
            layout.Row(
                layout.Column(
                    common_layout.SubmitClearLayout(
                        submit_text=submit_text.capitalize(),
                        submit_css_class='col-5 col-lg-6 col-xl-3',
                        reset_css_class='col-5 d-lg-none',
                    ),
                ),
            ),
            layout.Row(
                common_layout.Button(
                    content=_('go back').capitalize(),
                    css_class='btn-dark col-11 col-md-7 col-lg-6 col-xl-3',
                    action=JavaScriptActions.GO_BACK.value,
                    icon='ic-arrow-left',
                ),
                css_class='justify-content-around mt-3 mt-md-5 mt-lg-3',
            ),
        )


class SessionFormLayout(layout.Layout):
    def __init__(self, submit_text=_('create')):
        super().__init__(
            bootstrap.TabHolder(
                bootstrap.Tab(
                    _('basic information').title(),
                    layout.Row(
                        layout.Column('name'),
                        layout.Column('system'),
                        layout.Column('world'),
                    ),
                    layout.Row(
                        layout.Column(
                            layout.Field(
                                'plot',
                                placeholder=cfl(_('what will happen in this session?')),
                                style='resize: none'
                            ),
                        ),
                    ),
                ),
                bootstrap.Tab(
                    _('next session').title(),
                    layout.Row(
                        layout.Column('next_game'),
                    )
                ),
                bootstrap.Tab(
                    _('invite players').title(),
                    layout.Row(
                        layout.Column(
                            layout.Field(
                                'email_invitations',
                                placeholder='worldo@oar.com\ndungeon@fog.com\ndude@tabern.com',
                                style='resize: none',
                            ),
                        ),
                    ),
                ),
            ),
            layout.Row(
                layout.Column(
                    common_layout.SubmitClearLayout(
                        submit_text=submit_text.capitalize(),
                        reset_button=False,
                        submit_css_class='col-5 col-lg-6 col-xl-3',
                    ),
                ),
            ),
            layout.Row(
                common_layout.Button(
                    content=_('go back').capitalize(),
                    css_class='btn-dark col-11 col-md-7 col-lg-6 col-xl-3',
                    action=JavaScriptActions.GO_BACK.value,
                    icon='ic-arrow-left',
                ),
                css_class='justify-content-around mt-3 mt-md-5 mt-lg-3',
            ),
        )
