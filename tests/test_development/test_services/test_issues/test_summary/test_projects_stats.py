# -*- coding: utf-8 -*-

from datetime import datetime

from django.utils import timezone

from apps.development.models.issue import Issue
from apps.development.models.milestone import MilestoneState
from apps.development.services.issue.summary import (
    get_issues_summary,
    get_project_summaries,
)
from apps.development.services.issue.summary.project import get_min_due_date
from tests.test_development.factories import (
    IssueFactory,
    ProjectFactory,
    ProjectGroupFactory,
    ProjectMilestoneFactory,
)
from tests.test_development.test_services.test_issues.test_summary.helpers import (  # noqa: E501
    checkers,
)


def test_project_summary(user):
    projects = ProjectFactory.create_batch(2)

    IssueFactory.create_batch(
        5,
        user=user,
        total_time_spent=300,
        time_estimate=400,
        project=projects[0],
        due_date=datetime.now().date(),
    )

    IssueFactory.create_batch(
        3,
        user=user,
        total_time_spent=100,
        time_estimate=400,
        project=projects[1],
        due_date=datetime.now().date(),
    )

    summary = get_issues_summary(
        Issue.objects.filter(user=user),
        due_date=datetime.now().date(),
        user=user,
    )

    summary.projects = get_project_summaries(summary.queryset)

    assert len(summary.projects) == 2
    checkers.check_project_stats(
        summary,
        projects[0],
        issues_opened_count=5,
        percentage=5 / 8,
        remains=500,
    )

    checkers.check_project_stats(
        summary,
        projects[1],
        issues_opened_count=3,
        percentage=3 / 8,
        remains=900,
    )


def test_sort_projects_by_milestone_flat(db):
    projects = []
    for days in range(3):
        milestone = ProjectMilestoneFactory(state=MilestoneState.ACTIVE)
        ProjectMilestoneFactory(
            owner=milestone.owner,
            due_date=timezone.now() - timezone.timedelta(days=days),
        )
        ProjectMilestoneFactory(
            owner=milestone.owner,
            due_date=timezone.now() + timezone.timedelta(days=days),
            state=MilestoneState.ACTIVE,
        )

        projects.append(milestone.owner)

    expected = [project.id for project in projects]
    actual = [project.id for project in sorted(projects, key=get_min_due_date)]

    assert expected == actual


def test_sort_projects_by_milestone_neested(db):
    projects = []
    for days in range(3):
        group = ProjectGroupFactory.create(parent=ProjectGroupFactory.create())
        project = ProjectFactory.create(group=group)

        ProjectMilestoneFactory.create(state=MilestoneState.ACTIVE)
        ProjectMilestoneFactory.create(
            owner=group.parent,
            due_date=timezone.now() - timezone.timedelta(days=days),
            state=MilestoneState.ACTIVE,
        )
        ProjectMilestoneFactory.create(
            owner=group.parent,
            due_date=timezone.now() + timezone.timedelta(days=days),
            state=MilestoneState.ACTIVE,
        )

        projects.append(project)

    expected = [project.id for project in projects][::-1]
    actual = [project.id for project in sorted(projects, key=get_min_due_date)]

    assert expected == actual
