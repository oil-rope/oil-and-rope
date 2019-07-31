from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext as _


class DiscordUser(models.Model):

    identifier = models.CharField(_("Identifier"), max_length=100, primary_key=True)
    nick = models.CharField(_("Nick"), max_length=50)

    class Meta:
        verbose_name = _("discorduser")
        verbose_name_plural = _("discordusers")

    def __str__(self):
        return self.nick

    def get_absolute_url(self):
        return reverse("bot:discorduser_detail", kwargs={"pk": self.pk})
