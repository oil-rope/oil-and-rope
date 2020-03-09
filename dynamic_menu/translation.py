from modeltranslation.translator import TranslationOptions, register

from . import models


@register(models.DynamicMenu)
class DynamicMenuTranslationOptions(TranslationOptions):
    """
    Configures how model must be translated.
    """

    fields = ('name', 'description', )
