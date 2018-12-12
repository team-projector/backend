from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.db.mixins import GitlabEntityMixin
from apps.development.db.managers import IssueManager, ProjectGroupManager, ProjectManager
from apps.users.models import User


class ProjectGroup(GitlabEntityMixin):
    title = models.CharField(max_length=255, verbose_name=_('VN__TITLE'), help_text=_('HT__TITLE'))
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


class Issue(GitlabEntityMixin):
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

    labels = ArrayField(models.CharField(max_length=255, blank=True), null=True, blank=True,
                        verbose_name=_('VN__LABELS'), help_text=_('HT__LABELS'))

    created_at = models.DateTimeField(null=True, blank=True)

    objects = IssueManager()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('VN__ISSUE')
        verbose_name_plural = _('VN__ISSUES')
        ordering = ('title',)
