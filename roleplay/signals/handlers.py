from django.apps import apps
from django.db.models.signals import pre_save
from django.dispatch import receiver

from common.constants import models as constants

Chat = apps.get_model(constants.CHAT)
Campaign = apps.get_model(constants.ROLEPLAY_CAMPAIGN)


@receiver(pre_save, sender=Campaign)
def campaign_pre_save(sender, instance, *args, **kwargs):
    """
    Since Chat is obligatory but it doesn't make sense to have the user creating chats we just create one
    automatically and assign it to the campaign.
    """

    if not instance.chat_id:
        instance.chat = Chat.objects.create(
            name=f'{instance.name} Chat',
            discord_id=instance.discord_channel_id,
        )
