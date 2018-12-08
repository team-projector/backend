from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.db.mixins import GitlabEntityMixin
from apps.users.models import User


class ProjectGroup(GitlabEntityMixin):
    title = models.CharField(max_length=255, verbose_name=_('VN__TITLE'), help_text=_('HT__TITLE'))
    parent = models.ForeignKey('self', models.CASCADE, null=True, blank=True, verbose_name=_('VN__PARENT'),
                               help_text=_('HT__PARENT'))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('VN__PROJECT_GROUP')
        verbose_name_plural = _('VN__PROJECT_GROUPS')
        ordering = ('title',)


class Project(GitlabEntityMixin):
    title = models.CharField(max_length=255, verbose_name=_('VN__TITLE'), help_text=_('HT__TITLE'))
    group = models.ForeignKey(ProjectGroup, models.SET_NULL, null=True, blank=True,
                              verbose_name=_('VN__GROUP'), help_text=_('HT__GROUP'))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('VN__PROJECT')
        verbose_name_plural = _('VN__PROJECTS')
        ordering = ('title',)


class Issue(GitlabEntityMixin):
    title = models.CharField(max_length=255, verbose_name=_('VN__TITLE'), help_text=_('HT__TITLE'))
    project = models.ForeignKey(Project, models.SET_NULL, null=True, blank=True,
                                verbose_name=_('VN__PROJECT'), help_text=_('HT__PROJECT'))

    time_estimate = models.PositiveIntegerField(null=True, verbose_name=_('VN__TIME_ESTIMATE'),
                                                help_text=_('HT__TIME_ESTIMATE'))

    time_spend = models.PositiveIntegerField(null=True, verbose_name=_('VN__TIME_SPEND'),
                                             help_text=_('HT__TIME_SPEND'))

    employee = models.ForeignKey(User, models.SET_NULL, null=True, blank=True, verbose_name=_('VN__EMPLOYEE'),
                                 help_text=_('HT__EMPLOYEE'))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('VN__ISSUE')
        verbose_name_plural = _('VN__ISSUES')
        ordering = ('title',)
