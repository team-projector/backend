# -*- coding: utf-8 -*-

import types
from datetime import datetime
from typing import Iterable, List

from actstream.models import Action
from django.apps import apps

from apps.core.activity.verbs import (
    ACTION_GITLAB_CALL_API,
    ACTION_GITLAB_WEBHOOK_TRIGGERED,
)
from apps.core.models.mixins import GitlabEntityMixin
from apps.development.models import Issue


class GlServiceStatus:
    """Gitlab service status."""

    name: str
    time: datetime


class GlStatus:
    """Gitlab status."""

    services: Iterable[GlServiceStatus] = []
    last_issues: Iterable[Issue] = []
    last_sync: datetime


def get_gitlab_sync_status() -> GlStatus:
    """Get Gitlab sync status."""
    provider = GlStatusProvider()
    return provider.get_status()


ACTIONS_MAPS = types.MappingProxyType({
    "web_hooks": ACTION_GITLAB_WEBHOOK_TRIGGERED,
    "api": ACTION_GITLAB_CALL_API,
})


class GlStatusProvider:
    """Gitlab status provider."""

    def get_status(self) -> GlStatus:
        """Get status."""
        status = GlStatus()
        status.last_sync = self._get_last_sync()
        status.last_issues = self._get_last_issues()
        status.services = self._get_services_stats()

        return status

    @classmethod
    def _get_last_issues(cls, count: int = 10) -> List[Issue]:
        return list(Issue.objects.order_by("-gl_last_sync")[:count])

    @classmethod
    def _get_last_sync(cls) -> datetime:
        querysets = [
            model.objects.filter(
                gl_last_sync__isnull=False,
            ).values("gl_last_sync")
            for model in apps.get_models()
            if issubclass(model, GitlabEntityMixin)
        ]

        gl_last_sync_qs = querysets[0].union(
            *querysets[1:],
        ).order_by(
            "-gl_last_sync",
        ).first() or {}

        return gl_last_sync_qs.get("gl_last_sync")  # type: ignore

    @classmethod
    def _get_services_stats(cls) -> Iterable[GlServiceStatus]:
        stats = []

        for name, verb in ACTIONS_MAPS.items():
            action = Action.objects.filter(verb=verb).order_by(
                "-timestamp",
            ).first()

            if action:
                service_status = GlServiceStatus()
                service_status.name = name
                service_status.time = action.timestamp

                stats.append(service_status)

        return stats
