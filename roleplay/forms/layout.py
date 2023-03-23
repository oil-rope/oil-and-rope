from crispy_forms import bootstrap, layout
from django.utils.translation import gettext_lazy as _

from common.enums import AvailableIcons, JavaScriptActions
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
                    icon=AvailableIcons.ARROW_LEFT,
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
                    icon=AvailableIcons.ARROW_LEFT,
                ),
                css_class='justify-content-around mt-3 mt-md-5 mt-lg-3',
            ),
        )


class CampaignFormLayout(layout.Layout):
    def __init__(self, submit_text):
        super().__init__(
            bootstrap.TabHolder(
                bootstrap.Tab(
                    _('basic information').capitalize(),
                    layout.Row(
                        layout.Column(
                            layout.Field('place'),
                        ),
                    ),
                    layout.Row(
                        layout.Column(
                            layout.Field('is_public'),
                            css_class='col-12',
                        ),
                        layout.Column(
                            layout.Field('name', placeholder='The Incredible Adventures of...'),
                        ),
                        layout.Column(
                            layout.Field('summary'),
                        ),
                        layout.Column(
                            layout.Field('system'),
                        ),
                    ),
                    layout.Row(
                        layout.Column(
                            layout.Field(
                                'description',
                                placeholder=cfl(_('tell us about this adventure!')),
                                style='resize: none',
                            ),
                            css_class='col-md-12',
                        ),
                        layout.Column(
                            layout.Field(
                                'gm_info',
                                placeholder=_('write something that game masters need to know...').capitalize(),
                                style='resize: none',
                            ),
                            css_class='col-md-12',
                        ),
                    ),
                    layout.Row(
                        layout.Column(
                            layout.Field('cover_image'),
                        ),
                    ),
                ),
                bootstrap.Tab(
                    _('date settings').capitalize(),
                    layout.Row(
                        layout.Column(
                            layout.Field('start_date'),
                        ),
                        layout.Column(
                            layout.Field('end_date'),
                        ),
                    ),
                ),
                bootstrap.Tab(
                    _('invite players').capitalize(),
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
                        submit_css_class='col-11 col-md-5 col-lg-4 col-xl-3',
                    ),
                ),
            ),
            layout.Row(
                common_layout.Button(
                    content=_('go back').capitalize(),
                    css_class='btn-dark col-11 col-md-5 col-lg-4 col-xl-3',
                    action=JavaScriptActions.GO_BACK.value,
                    icon=AvailableIcons.ARROW_LEFT,
                ),
                css_class='justify-content-around mt-2 mt-md-5 mt-lg-3',
            ),
        )


class SessionFormLayout(layout.Layout):
    def __init__(self, submit_text):
        super().__init__(
            layout.Row(
                layout.Column(layout.Field('name'), css_class='col-md-4'),
                layout.Column(layout.Field('plot'), css_class='col-md-4'),
                layout.Column(layout.Field('next_game'), css_class='col-md-4'),
                layout.Column(layout.Field('description', style='resize: none'), css_class='col-md-6'),
                layout.Column(layout.Field('gm_info', style='resize: none'), css_class='col-md-6'),
                layout.Column(layout.Field('image')),
            ),
            layout.Row(
                layout.Column(
                    layout.Submit('submit', submit_text, css_class='btn btn-primary w-100'),
                    css_class='col-11 col-md-5 col-lg-4 col-xl-3'
                ),
                layout.Div(css_class='d-none d-xl-block w-100 my-2'),
                layout.Column(
                    common_layout.Button(
                        content=_('go back').capitalize(),
                        css_class='btn-dark w-100',
                        action=JavaScriptActions.GO_BACK,
                        icon=AvailableIcons.ARROW_LEFT,
                    ),
                    css_class='col-11 col-md-5 col-lg-4 col-xl-3 mt-3 mt-md-0'
                ),
                css_class='justify-content-around mt-2 mt-md-5 mt-lg-3',
            ),
        )


class RaceFormLayout(layout.Layout):
    def __init__(self, submit_text):
        super().__init__(
            bootstrap.TabHolder(
                bootstrap.Tab(
                    _('basic information').title(),
                    layout.Row(
                        layout.Column('name'),
                    ),
                    layout.Row(
                        layout.Column('description'),
                    ),
                    layout.Row(
                        layout.Column('image'),
                    ),
                ),
                bootstrap.Tab(
                    _('attributes').title(),
                    layout.Row(
                        layout.Column('strength'),
                        layout.Column('dexterity'),
                        layout.Column('constitution'),
                        layout.Column('intelligence'),
                        layout.Column('wisdom'),
                        layout.Column('charisma'),
                        layout.Column('affected_by_armor', css_class='col-3'),
                    ),
                    layout.Row(
                        layout.Column('users')
                    )
                ),
            ),
            layout.Row(
                layout.Column(
                    common_layout.SubmitClearLayout(
                        submit_text=submit_text.capitalize(),
                        submit_css_class='col-5 col-lg-6',
                        reset_css_class='col-5 d-lg-none',
                    ),
                ),
                css_class='justify-content-md-center',
            ),
        )


class RacePlaceFormLayout(layout.Layout):
    def __init__(self):
        super().__init__(
            layout.Row(
                layout.Column(layout.Field('place')),
                layout.Column(layout.Field('name')),
            ),
            layout.Row(
                layout.Column(layout.Field('description', style='resize: none')),
            ),
            layout.Row(
                bootstrap.Accordion(
                    bootstrap.AccordionGroup(
                        _('Stats'),
                        layout.Row(
                            layout.Column(layout.Field('strength')),
                            layout.Column(layout.Field('dexterity')),
                            layout.Column(layout.Field('constitution')),
                            layout.Column(layout.Field('intelligence')),
                            layout.Column(layout.Field('wisdom')),
                            layout.Column(layout.Field('charisma')),
                            css_class='row-cols-3',
                        ),
                        layout.Row(
                            layout.Column(layout.Field('affected_by_armor')),
                        ),
                        active=False,
                    ),
                ),
            ),
        )


class RaceCampaignFormLayout(layout.Layout):
    def __init__(self):
        super().__init__(
            layout.Row(
                layout.Column(layout.Field('campaign')),
                layout.Column(layout.Field('name')),
            ),
            layout.Row(
                layout.Column(layout.Field('description', style='resize: none')),
            ),
            layout.Row(
                bootstrap.Accordion(
                    bootstrap.AccordionGroup(
                        _('Stats'),
                        layout.Row(
                            layout.Column(layout.Field('strength')),
                            layout.Column(layout.Field('dexterity')),
                            layout.Column(layout.Field('constitution')),
                            layout.Column(layout.Field('intelligence')),
                            layout.Column(layout.Field('wisdom')),
                            layout.Column(layout.Field('charisma')),
                            css_class='row-cols-3',
                        ),
                        layout.Row(
                            layout.Column(layout.Field('affected_by_armor')),
                        ),
                        active=False,
                    ),
                ),
            ),
        )
