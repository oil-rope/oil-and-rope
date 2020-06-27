import json
import logging
from collections import defaultdict
from urllib.parse import urlparse

from django.conf import settings
from django.http import HttpResponseForbidden, JsonResponse, RawPostDataException
from django.utils.translation import gettext_lazy as _
from django.views.generic import View
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from bot.discord_api.models import User

LOGGER = logging.getLogger(__name__)


class SendMessageToDiscordUserView(View):
    http_method_names = ['post']
    message_content = None
    required_arguments = ['message_content', 'discord_user_id']

    def dispatch(self, request, *args, **kwargs):
        if '*' in settings.ALLOWED_HOSTS:
            return super().dispatch(request, *args, **kwargs)

        # We will allow requests only from ALLOWED_HOSTS
        origin_ip = request.headers.get('Origin')
        if origin_ip:
            origin_ip = urlparse(origin_ip).netloc
        if not origin_ip or origin_ip not in (settings.ALLOWED_HOSTS):
            if origin_ip:
                LOGGER.info('Access denied from %s.', origin_ip)
            else:
                LOGGER.info('Not Origin header given.')
            return HttpResponseForbidden()

        return super().dispatch(request, *args, **kwargs)

    def handle_post_data(self, request):
        """
        Check if all required arguments are in POST data.
        """

        data = defaultdict(list)

        if request.POST:
            self.content = request.POST
        else:
            try:
                self.content = json.loads(request.body)
            except RawPostDataException:
                self.content = {}

        for argument in self.required_arguments:
            if argument not in self.content:
                data['errors'].append(_('Please set \'{}\'').format(argument) + '.')

        return data

    def get_discord_user(self):
        """
        Gets DiscordApi User from ID.
        """

        discord_user_id = self.content['discord_user_id']
        discord_user = User(discord_user_id)
        return discord_user

    def get_message(self):
        if self.message_content:
            # Special case when declaring message on view
            # TODO: Remove 'pragma: no cover' when a view that uses message_content attribute exists
            self.message_content  # pragma: no cover
        return self.content['message_content']

    def send_message(self, discord_user):
        """
        Sends the message and returns a :class:`Message` object with the message created.
        """

        message = self.get_message()
        msg = discord_user.send_message(message)
        return msg

    def post(self, request, *args, **kwargs):
        data_errors = self.handle_post_data(request)

        if 'errors' in data_errors:
            return JsonResponse(data=data_errors, status=HTTP_400_BAD_REQUEST)

        discord_user = self.get_discord_user()
        message = self.send_message(discord_user)
        data = message.json_response

        return JsonResponse(data=data, status=HTTP_201_CREATED)


class SendInvitationView(SendMessageToDiscordUserView):
    required_arguments = ['discord_user_id']

    def get_message(self):
        msg = _('You are almost ready to start your adventure.') + '\n'
        msg += _('Type {command} to get your invitation').format(
            command=f'`{settings.BOT_COMMAND_PREFIX}invite`'
        )
        return msg
