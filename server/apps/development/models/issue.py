from collections import defaultdict
from datetime import datetime
from typing import DefaultDict, Optional

from django.db import models
from django.db.models import Max
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from apps.core.db.mixins import GitlabEntityMixin, GitlabInternalIdMixin
from apps.development.utils.parsers import parse_date
from apps.payroll.db.mixins import SpentTimesMixin
from apps.users.models import User
from .label import Label
from .note import Note
from .project import Project
from .epic import Epic
from ..db.managers import IssueManager
from ..db.mixins import NotableMixin

STATE_CLOSED = 'closed'
STATE_OPENED = 'opened'


class Issue(NotableMixin,
            SpentTimesMixin,
            GitlabEntityMixin,
            GitlabInternalIdMixin):
    title = models.CharField(
        max_length=255,
        verbose_name=_('VN__TITLE'),
        help_text=_('HT__TITLE')
    )

    time_estimate = models.PositiveIntegerField(
        null=True,
        verbose_name=_('VN__TIME_ESTIMATE'),
        help_text=_('HT__TIME_ESTIMATE')
    )

    total_time_spent = models.PositiveIntegerField(
        null=True,
        verbose_name=_('VN__TOTAL_TIME_SPENT'),
        help_text=_('HT__TOTAL_TIME_SPENT')
    )

    state = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('VN__STATE'),
        help_text=_('HT__STATE')
    )

    created_at = models.DateTimeField(
        null=True,
        blank=True
    )

    updated_at = models.DateTimeField(
        null=True,
        blank=True
    )

    closed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    due_date = models.DateField(
        null=True,
        blank=True
    )

    labels = models.ManyToManyField(
        Label,
        related_name='issues',
        blank=True
    )

    project = models.ForeignKey(
        Project,
        models.SET_NULL,
        null=True,
        blank=True,
        related_name='issues',
        verbose_name=_('VN__PROJECT'),
        help_text=_('HT__PROJECT')
    )

    user = models.ForeignKey(
        User,
        models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('VN__USER'),
        help_text=_('HT__USER')
    )

    milestone = models.ForeignKey(
        'Milestone',
        models.CASCADE,
        null=True,
    )

    epic = models.ForeignKey(
        Epic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    participants = models.ManyToManyField(
        User,
        blank=True,
        related_name='participant_issues',
    )

    objects = IssueManager()

    class Meta:
        verbose_name = _('VN__ISSUE')
        verbose_name_plural = _('VN__ISSUES')
        ordering = ('-created_at',)

    def __str__(self):
        return self.title

    @cached_property
    def last_note_date(self) -> datetime:
        return self.notes.aggregate(last_created=Max('created_at'))['last_created']

    @property
    def time_remains(self) -> Optional[int]:
        if self.time_estimate is not None and self.total_time_spent is not None:
            return max(self.time_estimate - self.total_time_spent, 0)

    @property
    def efficiency(self) -> Optional[float]:
        if self.total_time_spent and self.time_estimate:
            return self.time_estimate / self.total_time_spent

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

            SpentTime.objects.create(
                date=note_date,
                created_by=note.user,
                user=note.user,
                time_spent=time_spent,
                note=note,
                base=self
            )
