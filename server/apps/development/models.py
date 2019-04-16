from collections import defaultdict
from datetime import datetime
from typing import DefaultDict, Optional

from bitfield import BitField
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import Max
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from apps.core.db.mixins import GitlabEntityMixin, Timestamps
from apps.core.db.utils import Choices
from apps.development.utils.parsers import parse_date
from apps.payroll.db.mixins import SpentTimesMixin
from apps.users.models import User
from .db.managers import IssueManager, NoteManager, ProjectGroupManager, ProjectManager
from .db.mixins import NotableMixin


class Team(models.Model):
    title = models.CharField(max_length=255, verbose_name=_('VN__TITLE'), help_text=_('HT__TITLE'), unique=True)

    class Meta:
        verbose_name = _('VN__TEAM')
        verbose_name_plural = _('VN__TEAMS')
        ordering = ('title',)

    def __str__(self):
        return self.title


class TeamMember(models.Model):
    ROLES = Choices(
        ('leader', _('CH_LEADER')),
        ('developer', _('CH_DEVELOPER')),
        ('project_manager', _('CH_PM')),
    )

    team = models.ForeignKey(Team, models.CASCADE, related_name='members', verbose_name=_('VN__TEAM'),
                             help_text=_('HT__TEAM'))
    user = models.ForeignKey(User, models.CASCADE, related_name='team_members', verbose_name=_('VN__USER'),
                             help_text=_('HT__USER'))
    roles = BitField(flags=ROLES, default=0)

    class Meta:
        verbose_name = _('VN__TEAM_MEMBER')
        verbose_name_plural = _('VN__TEAM_MEMBERS')
        ordering = ('team', 'user')
        unique_together = ('team', 'user')

    def __str__(self):
        return f'{self.team}: {self.user}'


class ProjectMember(Timestamps):
    ROLE = Choices(
        ('developer', _('CH_DEVELOPER')),
        ('team_leader', _('CH_TEAM_LEADER')),
        ('project_manager', _('CH_PM')),
        ('customer', _('CH_CUSTOMER')),
    )

    user = models.ForeignKey(
        User,
        models.CASCADE
    )

    role = models.CharField(
        choices=ROLE,
        max_length=20,
        verbose_name=_('VN__ROLE'),
        help_text=_('HT__ROLE')
    )

    # Link to ProjectGroup or Project
    owner = GenericForeignKey()
    content_type = models.ForeignKey(ContentType, models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)

    class Meta:
        verbose_name = _('VN__PROJECT_MEMBER')
        verbose_name_plural = _('VN__PROJECT_MEMBERS')
        unique_together = ('user', 'role', 'object_id')


class ProjectGroup(GitlabEntityMixin):
    title = models.CharField(max_length=255, verbose_name=_('VN__TITLE'), help_text=_('HT__TITLE'))
    full_title = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('VN__FULL_TITLE'),
                                  help_text=_('HT__FULL_TITLE'))
    parent = models.ForeignKey('self', models.CASCADE, null=True, blank=True, verbose_name=_('VN__PARENT'),
                               help_text=_('HT__PARENT'))

    milestones = GenericRelation('Milestone', related_query_name='project_group')
    members = GenericRelation(ProjectMember, related_query_name='project_group')

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

    milestones = GenericRelation('Milestone', related_query_name='project')
    members = GenericRelation(ProjectMember, related_query_name='project')

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

    user = models.ForeignKey(User, models.SET_NULL, null=True, blank=True, verbose_name=_('VN__USER'),
                             help_text=_('HT__USER'))

    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    body = models.TextField(null=True)

    type = models.CharField(choices=TYPE, max_length=20, verbose_name=_('VN__TYPE'), help_text=_('HT__TYPE'))

    data = JSONField(encoder=DjangoJSONEncoder)

    objects = NoteManager()

    class Meta:
        verbose_name = _('VN__NOTE')
        verbose_name_plural = _('VN__NOTES')
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.user} [{self.created_at:%x}]: {self.type}'


STATE_CLOSED = 'closed'
STATE_OPENED = 'opened'


class Issue(NotableMixin,
            SpentTimesMixin,
            GitlabEntityMixin):
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

    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    due_date = models.DateField(null=True, blank=True)

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

            SpentTime.objects.create(date=note_date,
                                     created_by=note.user,
                                     user=note.user,
                                     time_spent=time_spent,
                                     note=note,
                                     base=self)


class Milestone(GitlabEntityMixin,
                Timestamps):
    title = models.CharField(
        max_length=255,
        verbose_name=_('VN__TITLE'),
        help_text=_('HT__TITLE')
    )
    description = models.TextField(
        verbose_name=_('VN__DESCRIPTION'),
        help_text=_('HT__DESCRIPTION')
    )
    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('VN__START_DATE'),
        help_text=_('HT__START_DATE')
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('VN__DUE_DATE'),
        help_text=_('HT__DUE_DATE')
    )
    budget = models.DecimalField(
        default=0,
        max_digits=12,
        decimal_places=2,
        verbose_name=_('VN__BUDGET'),
        help_text=_('HT__BUDGET')
    )

    # Link to ProjectGroup or Project
    owner = GenericForeignKey()
    content_type = models.ForeignKey(ContentType, models.CASCADE)
    object_id = models.PositiveIntegerField()


class Epic(Timestamps):
    title = models.CharField(
        max_length=255,
        verbose_name=_('VN__TITLE'),
        help_text=_('HT__TITLE')
    )
    description = models.TextField(
        verbose_name=_('VN__DESCRIPTION'),
        help_text=_('HT__DESCRIPTION')
    )
    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('VN__START_DATE'),
        help_text=_('HT__START_DATE')
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('VN__DUE_DATE'),
        help_text=_('HT__DUE_DATE')
    )
    budget = models.DecimalField(
        default=0,
        max_digits=12,
        decimal_places=2,
        verbose_name=_('VN__BUDGET'),
        help_text=_('HT__BUDGET')
    )

    milestone = models.ForeignKey(
        Milestone,
        models.CASCADE,
    )
