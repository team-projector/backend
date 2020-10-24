from datetime import datetime

from django.utils import timezone

from apps.development.models.issue import Issue
from apps.development.models.milestone import MilestoneState
from apps.development.models.project import ProjectState
from apps.development.services.issue.summary import (
    IssuesProjectSummary,
    get_issues_summary,
    get_project_summaries,
)
from apps.development.services.issue.summary.project import (
    ProjectIssuesSummary,
    sort_project_summaries,
)
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
    """
    Test project summary.

    :param user:
    """
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


def test_project_summary_without_is_active(user):
    """Test filtering active projects."""
    projects = ProjectFactory.create_batch(2, is_active=True)

    projects[1].is_active = False
    projects[1].save()

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

    summary_projects = get_project_summaries(
        summary.queryset,
        is_active=True,
    )

    assert len(summary_projects) == 1
    assert summary_projects[0].project == projects[0]


def test_project_summary_by_state(user):
    """Test filtering active projects."""
    projects = ProjectFactory.create_batch(
        2,
        is_active=True,
        state=ProjectState.DEVELOPING,
    )

    projects[1].state = (ProjectState.ARCHIVED,)
    projects[1].save()

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

    summary_projects = get_project_summaries(
        summary.queryset,
        state=ProjectState.DEVELOPING,
    )

    assert len(summary_projects) == 1
    assert summary_projects[0].project == projects[0]


def test_sort_projects_by_milestone_flat(db):
    """
    Test sort projects by milestone flat.

    :param db:
    """
    summaries = []
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

        summaries.append(
            IssuesProjectSummary(milestone.owner, ProjectIssuesSummary()),
        )

    expected = [summary.project.id for summary in summaries]
    actual = [
        summary.project.id
        for summary in sort_project_summaries(summaries, None)
    ]

    assert expected == actual


def test_sort_projects_by_milestone_nested(db):
    """
    Test sort projects by milestone nested.

    :param db:
    """
    summaries = []
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

        summaries.append(IssuesProjectSummary(project, ProjectIssuesSummary()))

    expected = [summary.project.id for summary in summaries][::-1]
    actual = [
        summary.project.id
        for summary in sort_project_summaries(summaries, None)
    ]

    assert expected == actual


def test_sort_by_remains_desc(db):
    """
    Test sort projects by milestone flat.

    :param db:
    """
    projects = ProjectFactory.create_batch(3)
    summaries = [
        IssuesProjectSummary(projects[0], ProjectIssuesSummary(remains=1000)),
        IssuesProjectSummary(projects[1], ProjectIssuesSummary(remains=0)),
        IssuesProjectSummary(projects[2], ProjectIssuesSummary(remains=3000)),
    ]

    assert sort_project_summaries(summaries, "-issues__remains") == [
        summaries[2],
        summaries[0],
        summaries[1],
    ]


def test_sort_by_remains_asc(db):
    """
    Test sort projects by milestone flat.

    :param db:
    """
    projects = ProjectFactory.create_batch(3)
    summaries = [
        IssuesProjectSummary(projects[0], ProjectIssuesSummary(remains=1000)),
        IssuesProjectSummary(projects[1], ProjectIssuesSummary(remains=0)),
        IssuesProjectSummary(projects[2], ProjectIssuesSummary(remains=3000)),
    ]

    assert sort_project_summaries(summaries, "issues__remains") == [
        summaries[1],
        summaries[0],
        summaries[2],
    ]
