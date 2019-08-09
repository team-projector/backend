from datetime import datetime, timedelta
from django.utils import timezone

from apps.development.services.summary.issues import (
    get_issues_summary, IssuesSummary
)
from apps.development.models import TeamMember, Project
from apps.development.models.issue import Issue, STATE_OPENED, STATE_CLOSED
from tests.test_development.factories import (
    IssueFactory, ProjectFactory, TeamFactory, TeamMemberFactory
)
from tests.test_payroll.factories import IssueSpentTimeFactory
from tests.test_users.factories import UserFactory


def test_issue_counts(user):
    IssueFactory.create_batch(
        5, user=user,
        state=STATE_OPENED,
        total_time_spent=0,
        due_date=datetime.now()
    )
    IssueFactory.create_batch(
        3, user=user,
        state=STATE_CLOSED,
        total_time_spent=0,
        due_date=datetime.now()
    )

    summary = get_issues_summary(
        Issue.objects.filter(user=user),
        due_date=None,
        user=user,
        team=None,
        project=None,
        state=None
    )

    _check_summary(summary, 8, 5, 3, 0, 0)


def test_problems(user):
    IssueFactory.create_batch(
        4,
        user=user,
        total_time_spent=0
    )
    IssueFactory.create_batch(
        1,
        user=user,
        total_time_spent=0,
        due_date=datetime.now()
    )

    IssueFactory.create_batch(
        2,
        user=UserFactory.create(),
        total_time_spent=0
    )

    summary = get_issues_summary(
        Issue.objects.filter(user=user),
        due_date=None,
        user=user,
        team=None,
        project=None,
        state=None
    )

    _check_summary(summary, 5, 5, 0, 0, 4)


def test_project_summary(user):
    project_1 = ProjectFactory()
    project_2 = ProjectFactory()

    IssueFactory.create_batch(
        5,
        user=user,
        total_time_spent=300,
        time_estimate=400,
        project=project_1,
        due_date=datetime.now().date()
    )

    IssueFactory.create_batch(
        3,
        user=user,
        total_time_spent=100,
        time_estimate=400,
        project=project_2,
        due_date=datetime.now().date()
    )

    summary = get_issues_summary(
        Issue.objects.filter(user=user),
        due_date=datetime.now().date(),
        user=user,
        team=None,
        project=None,
        state=None
    )

    assert len(summary.projects) == 2
    _check_project_stats(
        summary,
        project_1,
        issues_opened_count=5,
        percentage=5 / 8,
        remains=500
    )

    _check_project_stats(
        summary,
        project_2,
        issues_opened_count=3,
        percentage=3 / 8,
        remains=900
    )


def test_time_spents_by_user(user):
    issues = IssueFactory.create_batch(
        5, user=user,
        state=STATE_OPENED,
        due_date=datetime.now()
    )

    another_user = UserFactory.create()
    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=another_user,
        base=IssueFactory.create(user=another_user),
        time_spent=300
    )

    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=user,
        base=issues[0],
        time_spent=100
    )

    IssueSpentTimeFactory.create(
        date=datetime.now() - timedelta(days=2),
        user=user,
        base=issues[0],
        time_spent=200
    )

    summary = get_issues_summary(
        Issue.objects.filter(user=user),
        due_date=datetime.now().date(),
        user=user,
        team=None,
        project=None,
        state=None
    )

    _check_summary(summary, 5, 5, 0, 100, 0)


def test_time_spents_by_team(user):
    issues = IssueFactory.create_batch(
        5, user=user,
        state=STATE_OPENED,
        due_date=datetime.now()
    )

    another_user = UserFactory.create()

    team = TeamFactory.create()
    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.leader
    )

    TeamMemberFactory.create(
        user=another_user,
        team=TeamFactory.create(),
        roles=TeamMember.roles.developer
    )

    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=another_user,
        base=IssueFactory.create(user=another_user),
        time_spent=300
    )

    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=user,
        base=issues[0],
        time_spent=100
    )

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=2),
        user=user,
        base=issues[0],
        time_spent=200
    )

    summary = get_issues_summary(
        Issue.objects.filter(user=user),
        due_date=datetime.now().date(),
        user=user,
        team=team,
        project=None,
        state=None
    )

    _check_summary(summary, 5, 5, 0, 100, 0)


def test_time_spents_by_project(user):
    project_1 = ProjectFactory()
    project_2 = ProjectFactory()

    issues = IssueFactory.create_batch(
        5, user=user,
        state=STATE_OPENED,
        due_date=datetime.now(),
        project=project_1
    )

    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=user,
        base=issues[0],
        time_spent=100
    )

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=2),
        user=user,
        base=issues[0],
        time_spent=200
    )

    another_user = UserFactory.create()
    issue_another_user = IssueFactory.create(
        user=another_user,
        state=STATE_OPENED,
        due_date=datetime.now(),
        project=project_2
    )

    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=another_user,
        base=issue_another_user,
        time_spent=300
    )

    summary = get_issues_summary(
        Issue.objects.filter(user=user),
        due_date=datetime.now().date(),
        user=user,
        team=None,
        project=project_1,
        state=None
    )

    _check_summary(summary, 5, 5, 0, 100, 0)

    summary = get_issues_summary(
        Issue.objects.filter(user=another_user),
        due_date=datetime.now().date(),
        user=another_user,
        team=None,
        project=project_2,
        state=None
    )

    _check_summary(summary, 1, 1, 0, 300, 0)


def test_time_spents_by_state(user):
    issue_opened = IssueFactory.create(
        user=user,
        due_date=datetime.now(),
        state=STATE_OPENED
    )

    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=user,
        base=issue_opened,
        time_spent=100
    )
    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=2),
        user=user,
        base=issue_opened,
        time_spent=200
    )

    issue_closed = IssueFactory.create(
        user=user,
        due_date=datetime.now(),
        state=STATE_CLOSED
    )

    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=user,
        base=issue_closed,
        time_spent=400
    )

    summary = get_issues_summary(
        Issue.objects.filter(user=user),
        due_date=datetime.now().date(),
        user=user,
        team=None,
        project=None,
        state=STATE_OPENED
    )

    _check_summary(summary, 2, 1, 1, 100, 0)

    summary = get_issues_summary(
        Issue.objects.filter(user=user),
        due_date=datetime.now().date(),
        user=user,
        team=None,
        project=None,
        state=STATE_CLOSED
    )

    _check_summary(summary, 2, 1, 1, 400, 0)


def _check_summary(data: IssuesSummary,
                   count: int,
                   opened_count: int,
                   closed_count: int,
                   time_spent: int,
                   problems_count: int):
    assert data.count == count
    assert data.opened_count == opened_count
    assert data.closed_count == closed_count
    assert data.time_spent == time_spent
    assert data.problems_count == problems_count


def _check_project_stats(data: IssuesSummary,
                         project: Project,
                         issues_opened_count: int,
                         percentage: float,
                         remains: int):
    stats = next((
        item
        for item in data.projects
        if item.project == project
    ), None)

    assert stats is not None
    assert stats.issues.opened_count == issues_opened_count
    assert stats.issues.percentage == percentage
    assert stats.issues.remains == remains
