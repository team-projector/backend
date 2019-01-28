from django.db import models
from django.utils import timezone


class ProjectGroupManager(models.Manager):
    def sync_gitlab(self, gl_id, **kwargs):
        kwargs['gl_last_sync'] = timezone.now()

        return self.update_or_create(gl_id=gl_id, defaults=kwargs)


class ProjectManager(models.Manager):
    def sync_gitlab(self, gl_id, **kwargs):
        kwargs['gl_last_sync'] = timezone.now()

        return self.update_or_create(gl_id=gl_id, defaults=kwargs)


class IssueManager(models.Manager):
    def sync_gitlab(self, gl_id, **kwargs):
        kwargs['gl_last_sync'] = timezone.now()

        return self.update_or_create(gl_id=gl_id, defaults=kwargs)


class NoteManager(models.Manager):
    def sync_gitlab(self, gl_note, issue):
        from ..utils.loaders import extract_user_from_data
        from ..utils.notes import read_note
        from ..utils.parsers import parse_datetime

        note = issue.notes.filter(gl_id=gl_note.id).first()
        if note:
            return note

        parse_data = read_note(gl_note)
        if not parse_data:
            return

        return self.create(
            gl_id=gl_note.id,
            type=parse_data.type,
            created_at=parse_datetime(gl_note.created_at),
            user=extract_user_from_data(gl_note.author),
            content_object=issue,
            data=parse_data.data,
        )
