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
