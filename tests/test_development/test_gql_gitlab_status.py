from datetime import timedelta
from django.utils import timezone

from apps.core.activity.verbs import ACTION_GITLAB_CALL_API, ACTION_GITLAB_WEBHOOK_TRIGGERED
from apps.core.tasks import add_action
from apps.development.models import Issue, Project
from apps.development.services.status.gitlab import get_gitlab_sync_status
from tests.test_development.factories import IssueFactory


def test_status(user):
    IssueFactory.create_batch(size=20)
    Issue.objects.update(updated_at=timezone.now())

    project = Project.objects.first()
    project.gl_last_sync = timezone.now() + timedelta(minutes=2)
    project.save()

    add_action.delay(sender_id=user.id, verb=ACTION_GITLAB_WEBHOOK_TRIGGERED)
    add_action.delay(sender_id=user.id, verb=ACTION_GITLAB_CALL_API)

    sync_status = get_gitlab_sync_status()

    assert sync_status.last_sync == project.gl_last_sync
    assert set(x.id for x in sync_status.last_issues) == \
           set(Issue.objects.order_by('-updated_at')[:10].values_list('id', flat=True))
