from typing import Any, Tuple

from django.db import models
from django.utils import timezone


class ProjectGroupManager(models.Manager):
    def sync_gitlab(self, gl_id, **kwargs) -> Tuple[Any, bool]:
        kwargs['gl_last_sync'] = timezone.now()

        return self.update_or_create(gl_id=gl_id, defaults=kwargs)


class ProjectManager(models.Manager):
    def sync_gitlab(self, gl_id, **kwargs) -> Tuple[Any, bool]:
        kwargs['gl_last_sync'] = timezone.now()

        return self.update_or_create(gl_id=gl_id, defaults=kwargs)


class IssueManager(models.Manager):
    def sync_gitlab(self, gl_id, **kwargs) -> Tuple[Any, bool]:
        kwargs['gl_last_sync'] = timezone.now()

        return self.update_or_create(gl_id=gl_id, defaults=kwargs)


class MergeRequestManager(models.Manager):
    def sync_gitlab(self, gl_id, **kwargs) -> Tuple[Any, bool]:
        kwargs['gl_last_sync'] = timezone.now()

        return self.update_or_create(gl_id=gl_id, defaults=kwargs)


class MilestoneManager(models.Manager):
    def sync_gitlab(self, gl_id, **kwargs) -> Tuple[Any, bool]:
        kwargs['gl_last_sync'] = timezone.now()

        return self.update_or_create(gl_id=gl_id, defaults=kwargs)


class NoteManager(models.Manager):
    def sync_gitlab(self, gl_note, issue) -> Any:
        from ..services.gitlab.users import extract_user_from_data
        from ..services.gitlab.notes import read_note
        from ..services.gitlab.parsers import parse_gl_datetime

        if issue.last_note_date and issue.last_note_date > parse_gl_datetime(gl_note.created_at):
            return

        parse_data = read_note(gl_note)
        if not parse_data:
            return

        note = issue.notes.filter(gl_id=gl_note.id).first()
        if note:
            return note

        return self.create(
            gl_id=gl_note.id,
            type=parse_data.type,
            body=gl_note.body,
            created_at=parse_gl_datetime(gl_note.created_at),
            updated_at=parse_gl_datetime(gl_note.updated_at),
            user=extract_user_from_data(gl_note.author),
            content_object=issue,
            data=parse_data.data,
        )
