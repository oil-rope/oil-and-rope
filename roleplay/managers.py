from django.db import models
from django.utils import timezone
from mptt.models import TreeManager
from mptt.querysets import TreeQuerySet

from .enums import DomainTypes, SiteTypes


class DomainManager(models.Manager):

    def subdomains(self):
        return super().get_queryset().filter(domain_type=DomainTypes.SUBDOMAIN)

    def domains(self):
        return super().get_queryset().filter(domain_type=DomainTypes.DOMAIN)


class CampaignQuerySet(models.QuerySet):
    """
    Specific manager for :class:`~roleplay.models.Campaign` that filters queryset by some common filters.
    """

    def with_votes(self):
        """
        Return all campaigns with votes annotated.
        The new :class:`~django.db.models.QuerySet` will have the following fields:
        `positive_votes`, `negative_votes` and `total_votes`.
        """

        return super().annotate(
            positive_votes=models.Count('votes', filter=models.Q(votes__is_positive=True)),
            negative_votes=models.Count('votes', filter=models.Q(votes__is_positive=False)),
            total_votes=models.F('positive_votes') - models.F('negative_votes'),
        )


CampaignManager = models.Manager.from_queryset(CampaignQuerySet)


class SessionQuerySet(models.QuerySet):
    """
    Specific manager for :class:`~roleplay.models.Session` that filters queryset by some common filters.
    """

    def finished(self):
        """
        Return all finished sessions.
        """

        return super().filter(next_game__date__lt=timezone.now())


SessionManager = models.Manager.from_queryset(SessionQuerySet)


class PlaceQuerySet(TreeQuerySet):
    def community_places(self):
        """
        Union places without user (community).

        :return: A QuerySet with all community_places.
        """

        return super().filter(is_public=True)

    def worlds(self):
        return super().filter(site_type=SiteTypes.WORLD)


PlaceManager = TreeManager.from_queryset(PlaceQuerySet)
