from django.urls import include, path

from . import views

app_name = 'bot'

BOT_UTILS = [
    path('send_message/', views.SendMessageToDiscordUserView.as_view(), name='send_message'),
    path('send_invitation/', views.SendInvitationView.as_view(), name='send_invitation')
]

urlpatterns = [
    path('utils/', include((BOT_UTILS, app_name), namespace='utils')),
]
