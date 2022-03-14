from crispy_forms import layout
from django.conf import settings
from django.shortcuts import reverse
from django.utils.translation import gettext_lazy as _

from common.forms import layout as common_layout
from common.templatetags.string_utils import capfirstletter as cfl


class LoginFormLayout(layout.Layout):
    def __init__(self):
        super().__init__(
            layout.Row(
                layout.Column(
                    layout.Field('username', css_class='text-light'),
                    css_class='col-sm-12 col-md-10 col-lg-8 col-xl-10'
                ),
                layout.Column(
                    layout.Field('password', css_class='text-light'),
                    css_class='col-sm-12 col-md-10 col-lg-8 col-xl-10'
                ),
                css_class='justify-content-md-around',
            ),
            layout.Row(
                layout.Submit('login', _('login').capitalize(), css_class='col col-md-9 btn-lg text-light'),
                layout.Div(css_class='w-100'),
                common_layout.Link(
                    content=_('login with %(social_media)s').capitalize() % {'social_media': 'Google'},
                    icon='ic-google',
                    url=reverse('google_login'),
                    css_class='btn-lg bg-light col col-md-9 mt-2',
                ),
                css_class='justify-content-md-around mt-md-3',
            )
        )


class SignUpFormLayout(layout.Layout):
    def __init__(self):
        super().__init__(
            layout.Row(
                layout.Column('username', css_class='col-12 col-lg-6 col-xl-5'),
                layout.Column('email', css_class='col-12 col-lg-6 col-xl-5'),
                css_class='justify-content-xl-between'
            ),
            layout.Row(
                layout.Column('password1', css_class='col-12 col-lg-6 col-xl-5'),
                layout.Column('password2', css_class='col-12 col-lg-6 col-xl-5'),
                css_class='justify-content-xl-between'
            ),
            layout.Row(
                layout.Column('discord_id', css_class='col-12 col-md-6 col-lg-6 col-xl-5'),
                common_layout.Link(
                    content=cfl(_('invite our bot to your server!')),
                    url=settings.BOT_INVITATION,
                    new_tab=True,
                    css_class='btn-info align-self-center col-12 col-md-6 col-lg-6 col-xl-5',
                ),
                css_class='justify-content-xl-between mb-5'
            ),
            layout.Row(
                layout.Column(
                    common_layout.SubmitClearLayout(reset_button=False, create_text=_('register').title()),
                    css_class='col-lg-8 col-xl-6'
                ),
                css_class='justify-content-lg-around'
            )
        )


class ResendEmailFormLayout(layout.Layout):
    def __init__(self):
        super().__init__(
            layout.Row(
                layout.Column('email', css_class='col-12 col-xl-8'),
                css_class='justify-content-around'
            ),
            layout.Row(
                layout.Column(
                    common_layout.SubmitClearLayout(reset_button=False, create_text=_('resend email').capitalize()),
                    css_class='col-md-10 col-lg-6'
                ),
                css_class='justify-content-md-around'
            )
        )


class PasswordResetFormLayout(layout.Layout):
    def __init__(self):
        super().__init__(
            layout.Row(
                layout.Column('email')
            ),
            layout.Row(
                layout.Column(
                    common_layout.SubmitClearLayout(reset_button=False, create_text=_('send email').capitalize()),
                )
            )
        )


class SetPasswordFormLayout(layout.Layout):
    def __init__(self):
        super().__init__(
            layout.Row(
                layout.Column('new_password1', css_class='col-12 col-lg-5'),
                layout.Column('new_password2', css_class='col-12 col-lg-5'),
                css_class='justify-content-around'
            ),
            layout.Row(
                layout.Column(
                    common_layout.SubmitClearLayout(reset_button=False, create_text=_('change password').capitalize()),
                    css_class='col-12 col-lg-6'
                ),
                css_class='justify-content-around'
            )
        )


class UserFormLayout(layout.Layout):
    def __init__(self):
        super().__init__(
            layout.Row(
                layout.Column(
                    layout.Row(
                        layout.Column('username'),
                        layout.Column('email'),
                    ),
                    layout.Row(
                        layout.Column('first_name'),
                        layout.Column('last_name'),
                    ),
                    layout.Row(
                        layout.Column('bio'),
                    ),
                    layout.Row(
                        layout.Column('birthday'),
                        layout.Column('language'),
                    ),
                    layout.Row(
                        layout.Column('web'),
                    ),
                    layout.Row(
                        layout.Column(
                            common_layout.SubmitClearLayout(
                                reset_button=False,
                                submit_text=_('update').capitalize(),
                                submit_css_class='col-sm-10 col-xl-8',
                            ),
                        ),
                        css_class='mt-md-2',
                    ),
                ),
                layout.Column(
                    layout.Row(
                        layout.Div(css_class='w-100'),
                        layout.Column('image'),
                        css_class='justify-content-around px-md-4',
                    ),
                ),
                css_class='flex-column-reverse flex-md-row'
            ),
        )
