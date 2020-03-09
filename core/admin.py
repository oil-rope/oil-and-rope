from django.contrib import admin


class TracingMixinAdmin(admin.ModelAdmin):
    """
    Manager for tracing features.
    """

    readonly_fields = ('entry_created_at', 'entry_updated_at')
