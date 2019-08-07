from django.db import models
from django.utils.translation import ugettext as _


class TracingMixin(models.Model):
    """
    This model makes a tracing for other models.

    Attributes
    -----------
    created_at: :class:`datetime.datetime`
        The date when the model was created.
    updated_at: :class:`datetime.datetime`
        Last time model was updated.
    """

    entry_created_at = models.DateTimeField(_("Entry created at"), auto_now=False, auto_now_add=True)
    entry_updated_at = models.DateTimeField(_("Entry updated at"), auto_now=True, auto_now_add=False)

    class Meta:
        abstract = True
        ordering = ['-created_at', 'updated_at']
