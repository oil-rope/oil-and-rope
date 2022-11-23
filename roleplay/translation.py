from modeltranslation.translator import TranslationOptions, register

from .models import TraitType


@register(TraitType)
class TraitTypeTranslationOptions(TranslationOptions):
    fields = ('name', 'description')
