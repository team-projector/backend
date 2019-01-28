from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.db.mixins import GitlabEntityMixin
from apps.core.db.utils import Choices
from apps.users.models import User
from .db.managers import IssueManager, NoteManager, ProjectGroupManager, ProjectManager
from .db.mixins import Notable


class ProjectGroup(GitlabEntityMixin):
    title = models.CharField(max_length=255, verbose_name=_('VN__TITLE'), help_text=_('HT__TITLE'))
    full_title = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('VN__FULL_TITLE'),
                                  help_text=_('HT__FULL_TITLE'))
    parent = models.ForeignKey('self', models.CASCADE, null=True, blank=True, verbose_name=_('VN__PARENT'),
                               help_text=_('HT__PARENT'))

    objects = ProjectGroupManager()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('VN__PROJECT_GROUP')
        verbose_name_plural = _('VN__PROJECT_GROUPS')
        ordering = ('title',)


class Project(GitlabEntityMixin):
    title = models.CharField(max_length=255, verbose_name=_('VN__TITLE'), help_text=_('HT__TITLE'))
    full_title = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('VN__FULL_TITLE'),
                                  help_text=_('HT__FULL_TITLE'))
    group = models.ForeignKey(ProjectGroup, models.SET_NULL, null=True, blank=True,
                              verbose_name=_('VN__GROUP'), help_text=_('HT__GROUP'))

    gl_last_issues_sync = models.DateTimeField(null=True, blank=True, verbose_name=_('VN__GITLAB_LAST_ISSUES_SYNC'),
                                               help_text=_('HT__GITLAB_LAST_ISSUES_SYNC'))

    objects = ProjectManager()

    def __str__(self):
        return self.full_title or self.title

    def save(self, *args, **kwargs):
        if not self.full_title:
            self.full_title = self.title

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('VN__PROJECT')
        verbose_name_plural = _('VN__PROJECTS')
        ordering = ('full_title', 'title')


class Label(models.Model):
    title = models.CharField(max_length=255, verbose_name=_('VN__TITLE'), help_text=_('HT__TITLE'))
    color = models.CharField(max_length=10, verbose_name=_('VN__COLOR'), help_text=_('HT__COLOR'))

    def __str__(self):
        return self.title


class Note(models.Model):
    TYPE = Choices(
        ('time_spend', 'Time spend'),
        ('reset_spend', 'Reset spend')
    )

    object_id = models.IntegerField()
    content_object = GenericForeignKey()
    content_type = models.ForeignKey(ContentType, models.CASCADE)

    gl_id = models.PositiveIntegerField(verbose_name=_('VN__GITLAB_ID'), help_text=_('HT__GITLAB_ID'))

    user = models.ForeignKey(User, models.SET_NULL, null=True, blank=True, verbose_name=_('VN__EMPLOYEE'),
                             help_text=_('HT__EMPLOYEE'))

    created_at = models.DateTimeField(null=True, blank=True)

    type = models.CharField(choices=TYPE, max_length=20, verbose_name=_('VN__TYPE'), help_text=_('HT__TYPE'))

    data = JSONField()

    objects = NoteManager()

    def __str__(self):
        return f'{self.user}: {self.type}'


class Issue(Notable,
            GitlabEntityMixin):
    title = models.CharField(max_length=255, verbose_name=_('VN__TITLE'), help_text=_('HT__TITLE'))
    project = models.ForeignKey(Project, models.SET_NULL, null=True, blank=True,
                                verbose_name=_('VN__PROJECT'), help_text=_('HT__PROJECT'))

    time_estimate = models.PositiveIntegerField(null=True, verbose_name=_('VN__TIME_ESTIMATE'),
                                                help_text=_('HT__TIME_ESTIMATE'))

    total_spent = models.PositiveIntegerField(null=True, verbose_name=_('VN__TOTAL_SPENT'),
                                                   help_text=_('HT__TOTAL_SPENT'))

    employee = models.ForeignKey(User, models.SET_NULL, null=True, blank=True, verbose_name=_('VN__EMPLOYEE'),
                                 help_text=_('HT__EMPLOYEE'))

    state = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('VN__STATE'),
                             help_text=_('HT__STATE'))

    created_at = models.DateTimeField(null=True, blank=True)

    due_date = models.DateField(null=True, blank=True)

    labels = models.ManyToManyField(Label, related_name='issues', blank=True)

    objects = IssueManager()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('VN__ISSUE')
        verbose_name_plural = _('VN__ISSUES')
        ordering = ('title',)
