from datetime import datetime
from typing import Iterable

from actstream.models import Action
from django.apps import apps

from apps.core.activity.verbs import (
    ACTION_GITLAB_CALL_API, ACTION_GITLAB_WEBHOOK_TRIGGERED,
)
from apps.core.models.mixins import GitlabEntityMixin
from apps.development.models import Issue


class GlServiceStatus:
    name: str
    time: datetime


class GlStatus:
    services: Iterable[GlServiceStatus] = []
    last_issues: Iterable[Issue] = []
    last_sync: datetime


def get_gitlab_sync_status() -> GlStatus:
    provider = GlStatusProvider()
    return provider.get_status()


ACTIONS_MAPS = {
    'web_hooks': ACTION_GITLAB_WEBHOOK_TRIGGERED,
    'api': ACTION_GITLAB_CALL_API,
}


class GlStatusProvider:
    def get_status(self) -> GlStatus:
        status = GlStatus()
        status.last_sync = self._get_last_sync()
        status.last_issues = self._get_last_issues()
        status.services = self._get_services_stats()

        return status

    @classmethod
    def _get_last_issues(cls, count: int = 10) -> Iterable[Issue]:
        return list(Issue.objects.order_by('-gl_last_sync')[:count])

    @classmethod
    def _get_last_sync(cls) -> datetime:
        querysets = [
            x.objects.filter(gl_last_sync__isnull=False).values('gl_last_sync')
            for x in apps.get_models()
            if issubclass(x, GitlabEntityMixin)
        ]
        value = querysets[0].union(*querysets[1:]).order_by(
            '-gl_last_sync',
        ).first() or {}
        return value.get('gl_last_sync')  # type: ignore

    @classmethod
    def _get_services_stats(cls) -> Iterable[GlServiceStatus]:
        stats = []

        for key, value in ACTIONS_MAPS.items():
            action = Action.objects.filter(verb=value).order_by(
                '-timestamp',
            ).first()

            if action:
                service_status = GlServiceStatus()
                service_status.name = key
                service_status.time = action.timestamp

                stats.append(service_status)

        return stats
