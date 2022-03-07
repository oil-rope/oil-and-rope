from crispy_forms import bootstrap, layout
from django.utils.translation import gettext_lazy as _

from common.forms import layout as common_layout


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
                        submit_css_class='col-5 col-lg-10',
                        reset_css_class='col-5 d-lg-none',
                    ),
                ),
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
                        submit_css_class='col-5 col-lg-6',
                        reset_css_class='col-5 d-lg-none',
                    ),
                )
            )
        )


class SessionFormLayout(layout.Layout):
    def __init__(self):
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
                        layout.Column('description'),
                    ),
                ),
                bootstrap.Tab(
                    _('next session').title(),
                    layout.Row(
                        layout.Column('next_game_date', css_class='col-6'),
                        layout.Column('next_game_time', css_class='col-6'),
                    )
                ),
                bootstrap.Tab(
                    _('invite players').title(),
                    layout.Row(
                        layout.Column(layout.Field('invited_players', id='playersInvitedContainer')),
                        layout.Column(
                            layout.Field('invite_player_input', id='invitePlayerInput'), css_class='align-self-end'
                        ),
                        bootstrap.StrictButton(
                            content=_('add').capitalize(),
                            css_class='btn-info col align-self-center', css_id='playerAddButton'
                        ),
                    ),
                ),
            ),
            layout.Row(
                layout.Column(
                    common_layout.SubmitClearLayout(reset_button=False),
                    css_class='col-md-6'
                ),
                css_class='justify-content-md-center',
            ),
        )
