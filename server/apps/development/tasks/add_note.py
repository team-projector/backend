from apps.development.models import Issue
from apps.development.services.note.gitlab import add_issue_note
from apps.users.models import User
from celery_app import app


@app.task
def add_issue_note_task(
    user_id: int,
    issue_id: int,
    message: str,
) -> None:
    """Run service for add note to issue."""
    add_issue_note(
        user=User.objects.get(id=user_id),
        issue=Issue.objects.get(id=issue_id),
        message=message,
    )
