from collections import defaultdict

from django.conf import settings
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views.generic import View
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from django.http import HttpResponseForbidden

from bot.discord_api.models import User


class SendMessageToDiscordUserView(View):
    http_method_names = ['post']
    required_arguments = ['message_content']

    def dispatch(self, request, *args, **kwargs):
        if '*' in settings.ALLOWED_HOSTS:
            return super().dispatch(request, *args, **kwargs)

        # We will allow requests only from ALLOWED_HOSTS
        try:
            client_ip = request.META['REMOTE_ADDR']
        except KeyError:  # pragma: no cover
            client_ip = request.META.get('HTTP_X_FORWARDED_FOR')
        finally:
            if not client_ip or client_ip not in (settings.ALLOWED_HOSTS):
                return HttpResponseForbidden()

        return super().dispatch(request, *args, **kwargs)

    def handle_post_data(self):
        """
        Check if all required arguments are in POST data.
        """

        data = defaultdict(list)
        for argument in self.required_arguments:
            if argument not in self.request.POST:
                data['errors'].append(_('Please set \'{}\'').format(argument))
        return data

    def get_discord_user(self):
        """
        Gets DiscordApi User from ID.
        """

        discord_user_id = self.kwargs['discord_user']
        discord_user = User(discord_user_id)
        return discord_user

    def send_message(self, discord_user):
        """
        Sends the message and returns a :class:`Message` object with the message created.
        """

        message = self.request.POST['message_content']
        msg = discord_user.send_message(message)
        return msg

    def post(self, request, *args, **kwargs):
        data_errors = self.handle_post_data()

        if 'errors' in data_errors:
            return JsonResponse(data=data_errors, status=HTTP_400_BAD_REQUEST)

        discord_user = self.get_discord_user()
        message = self.send_message(discord_user)
        data = message.json_response

        return JsonResponse(data=data, status=HTTP_201_CREATED)
