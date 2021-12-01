from django.apps import apps
from django.db import models

from common.constants import models as constants


class DynamicMenuManager(models.Manager):
    """
    Specific manager for Menus.
    """

    def from_user(self, user):
        Permission = apps.get_model(constants.PERMISSION_MODEL)

        if user.is_superuser:
            user_perms_menus = Permission.objects.values_list('menus', flat=True)
            menus = list(user_perms_menus)
        else:
            user_perms_menus = user.user_permissions.values_list('menus', flat=True)
            group_perms_menus = user.groups.values_list('permissions__menus', flat=True)
            menus = list(user_perms_menus) + list(group_perms_menus)

        # Getting all menus and union
        non_perms_menus = self.filter(permissions_required__isnull=True)
        menus = self.filter(pk__in=menus).union(non_perms_menus).distinct()
        menus = list(menus)

        # Filter by staff and superuser
        if not user.is_staff:
            menus = [menu for menu in menus if not menu.staff_required]

        return menus
