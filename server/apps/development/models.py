from collections import defaultdict
from typing import DefaultDict

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import Max
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from apps.core.db.mixins import GitlabEntityMixin
from apps.core.db.utils import Choices
from apps.development.utils.parsers import parse_date
from apps.payroll.db.mixins import SpentTimesMixin
from apps.users.models import User
from .db.managers import IssueManager, NoteManager, ProjectGroupManager, ProjectManager
from .db.mixins import NotableMixin


class ProjectGroup(GitlabEntityMixin):
    title = models.CharField(max_length=255, verbose_name=_('VN__TITLE'), help_text=_('HT__TITLE'))
    full_title = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('VN__FULL_TITLE'),
                                  help_text=_('HT__FULL_TITLE'))
    parent = models.ForeignKey('self', models.CASCADE, null=True, blank=True, verbose_name=_('VN__PARENT'),
                               help_text=_('HT__PARENT'))

    objects = ProjectGroupManager()

    class Meta:
        verbose_name = _('VN__PROJECT_GROUP')
        verbose_name_plural = _('VN__PROJECT_GROUPS')
        ordering = ('title',)

    def __str__(self):
        return self.title


class Project(GitlabEntityMixin):
    title = models.CharField(max_length=255, verbose_name=_('VN__TITLE'), help_text=_('HT__TITLE'))
    full_title = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('VN__FULL_TITLE'),
                                  help_text=_('HT__FULL_TITLE'))
    group = models.ForeignKey(ProjectGroup, models.SET_NULL, null=True, blank=True,
                              verbose_name=_('VN__GROUP'), help_text=_('HT__GROUP'))

    gl_last_issues_sync = models.DateTimeField(null=True, blank=True, verbose_name=_('VN__GITLAB_LAST_ISSUES_SYNC'),
                                               help_text=_('HT__GITLAB_LAST_ISSUES_SYNC'))

    objects = ProjectManager()

    class Meta:
        verbose_name = _('VN__PROJECT')
        verbose_name_plural = _('VN__PROJECTS')
        ordering = ('full_title', 'title')

    def __str__(self):
        return self.full_title or self.title

    def save(self, *args, **kwargs) -> None:
        if not self.full_title:
            self.full_title = self.title

        super().save(*args, **kwargs)


class Label(models.Model):
    title = models.CharField(max_length=255, verbose_name=_('VN__TITLE'), help_text=_('HT__TITLE'))
    color = models.CharField(max_length=10, verbose_name=_('VN__COLOR'), help_text=_('HT__COLOR'))

    class Meta:
        verbose_name = _('VN__LABEL')
        verbose_name_plural = _('VN__LABELS')

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
    updated_at = models.DateTimeField(null=True, blank=True)

    body = models.TextField(null=True)

    type = models.CharField(choices=TYPE, max_length=20, verbose_name=_('VN__TYPE'), help_text=_('HT__TYPE'))

    data = JSONField(encoder=DjangoJSONEncoder)

    objects = NoteManager()

    class Meta:
        verbose_name = _('VN__NOTE')
        verbose_name_plural = _('VN__NOTES')
        ordering = ('created_at',)

    def __str__(self):
        return f'{self.user}: {self.type}'


STATE_CLOSED = 'closed'
STATE_OPENED = 'opened'


class Issue(NotableMixin,
            SpentTimesMixin,
            GitlabEntityMixin):
    title = models.CharField(max_length=255, verbose_name=_('VN__TITLE'), help_text=_('HT__TITLE'))
    project = models.ForeignKey(Project, models.SET_NULL, null=True, blank=True,
                                verbose_name=_('VN__PROJECT'), help_text=_('HT__PROJECT'))

    time_estimate = models.PositiveIntegerField(null=True, verbose_name=_('VN__TIME_ESTIMATE'),
                                                help_text=_('HT__TIME_ESTIMATE'))

    total_time_spent = models.PositiveIntegerField(null=True, verbose_name=_('VN__TOTAL_TIME_SPENT'),
                                                   help_text=_('HT__TOTAL_TIME_SPENT'))

    employee = models.ForeignKey(User, models.SET_NULL, null=True, blank=True, verbose_name=_('VN__EMPLOYEE'),
                                 help_text=_('HT__EMPLOYEE'))

    state = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('VN__STATE'),
                             help_text=_('HT__STATE'))

    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    due_date = models.DateField(null=True, blank=True)

    labels = models.ManyToManyField(Label, related_name='issues', blank=True)

    objects = IssueManager()

    class Meta:
        verbose_name = _('VN__ISSUE')
        verbose_name_plural = _('VN__ISSUES')
        ordering = ('-created_at',)

    def __str__(self):
        return self.title

    @cached_property
    def last_note_date(self):
        return self.notes.aggregate(last_created=Max('created_at'))['last_created']

    @property
    def time_remains(self):
        if self.time_estimate is not None and self.total_time_spent is not None:
            return max(self.time_estimate - self.total_time_spent, 0)

    def adjust_spent_times(self) -> None:
        from apps.payroll.models import SpentTime

        users_spents: DefaultDict[int, int] = defaultdict(int)

        for note in self.notes.all().order_by('created_at'):
            time_spent = 0
            note_date = note.created_at.date()

            if note.type == Note.TYPE.reset_spend:
                time_spent = -users_spents[note.user_id]
                users_spents[note.user_id] = 0
            elif note.type == Note.TYPE.time_spend:
                time_spent = note.data['spent']
                note_date = parse_date(note.data['date'])

                users_spents[note.user_id] += note.data['spent']

            if SpentTime.objects.filter(note=note).exists():
                continue

            SpentTime.objects.create(date=note_date,
                                     created_at=note.created_at,
                                     updated_at=note.updated_at,
                                     employee=note.user,
                                     time_spent=time_spent,
                                     note=note,
                                     base=self)
