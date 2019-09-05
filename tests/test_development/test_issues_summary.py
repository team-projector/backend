from datetime import datetime, timedelta
from django.utils import timezone

from apps.development.graphql.resolvers import resolve_issues_summary
from apps.development.models import Team, TeamMember, Project, Milestone
from apps.development.models.issue import Issue, STATE_OPENED, STATE_CLOSED
from apps.development.services.summary.issues import (
    get_issues_summary, IssuesSummary
)
from apps.development.services.summary.issues_project import (
    get_min_due_date, get_project_summaries
)
from apps.development.services.summary.issues_team import get_team_summaries
from tests.test_development.factories import (
    IssueFactory, ProjectFactory, TeamFactory, TeamMemberFactory,
    ProjectMilestoneFactory, ProjectGroupFactory
)
from tests.test_development.factories_gitlab import AttrDict
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
        state=None,
        milestone=None
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
        state=None,
        milestone=None
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
        state=None,
        milestone=None
    )

    summary.projects = get_project_summaries(summary.queryset)

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


def test_team_summary(db):
    user_1 = UserFactory.create()
    team_1 = TeamFactory.create()
    TeamMemberFactory.create(
        user=user_1,
        team=team_1,
        roles=TeamMember.roles.developer
    )
    IssueFactory.create_batch(
        5,
        user=user_1,
        total_time_spent=300,
        time_estimate=400,
        due_date=datetime.now().date()
    )

    user_2 = UserFactory.create()
    team_2 = TeamFactory.create()
    TeamMemberFactory.create(
        user=user_2,
        team=team_2,
        roles=TeamMember.roles.developer
    )
    IssueFactory.create_batch(
        3,
        user=user_2,
        total_time_spent=100,
        time_estimate=400,
        due_date=datetime.now().date()
    )

    summary = get_issues_summary(
        Issue.objects.all(),
        due_date=None,
        user=None,
        team=None,
        project=None,
        state=None,
        milestone=None
    )

    summary.teams = get_team_summaries(summary.queryset)

    assert len(summary.teams) == 2
    _check_team_stats(
        summary,
        team_1,
        issues_opened_count=5,
        percentage=5 / 8,
        remains=500
    )
    _check_team_stats(
        summary,
        team_2,
        issues_opened_count=3,
        percentage=3 / 8,
        remains=900
    )


def test_sort_projects_by_milestone_flat(db):
    projs = []
    for n in range(3):
        m = ProjectMilestoneFactory(state=Milestone.STATE.active)
        ProjectMilestoneFactory(
            owner=m.owner,
            due_date=timezone.now() - timezone.timedelta(days=n),
        )
        ProjectMilestoneFactory(
            owner=m.owner,
            due_date=timezone.now() + timezone.timedelta(days=n),
            state=Milestone.STATE.active
        )

        projs.append(m.owner)

    results = sorted(projs, key=get_min_due_date)
    assert [projs[0].id, projs[1].id, projs[2].id] == [p.id for p in results]


def test_sort_projects_by_milestone_neested(db):
    projs = []
    for n in range(3):
        group = ProjectGroupFactory(parent=ProjectGroupFactory())
        proj = ProjectFactory(group=group)

        ProjectMilestoneFactory(state=Milestone.STATE.active)
        ProjectMilestoneFactory(
            owner=group.parent,
            due_date=timezone.now() - timezone.timedelta(days=n),
            state=Milestone.STATE.active
        )
        ProjectMilestoneFactory(
            owner=group.parent,
            due_date=timezone.now() + timezone.timedelta(days=n),
            state=Milestone.STATE.active
        )

        projs.append(proj)

    results = sorted(projs, key=get_min_due_date)
    assert [projs[2].id, projs[1].id, projs[0].id] == [p.id for p in results]


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
        state=None,
        milestone=None
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
        state=None,
        milestone=None
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
        state=None,
        milestone=None
    )

    _check_summary(summary, 5, 5, 0, 100, 0)

    summary = get_issues_summary(
        Issue.objects.filter(user=another_user),
        due_date=datetime.now().date(),
        user=another_user,
        team=None,
        project=project_2,
        state=None,
        milestone=None
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
        state=STATE_OPENED,
        milestone=None
    )

    _check_summary(summary, 2, 1, 1, 100, 0)

    summary = get_issues_summary(
        Issue.objects.filter(user=user),
        due_date=datetime.now().date(),
        user=user,
        team=None,
        project=None,
        state=STATE_CLOSED,
        milestone=None
    )

    _check_summary(summary, 2, 1, 1, 400, 0)


def test_time_spents_by_milestone(user):
    milestone_1 = ProjectMilestoneFactory.create()
    issue_1 = IssueFactory.create(
        user=user,
        due_date=datetime.now(),
        state=STATE_OPENED,
        milestone=milestone_1
    )
    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=user,
        base=issue_1,
        time_spent=100
    )

    milestone_2 = ProjectMilestoneFactory.create()
    issue_2 = IssueFactory.create(
        user=user,
        due_date=datetime.now(),
        state=STATE_OPENED,
        milestone=milestone_2
    )
    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=user,
        base=issue_2,
        time_spent=300
    )

    summary = get_issues_summary(
        Issue.objects.filter(user=user),
        due_date=datetime.now().date(),
        user=user,
        team=None,
        project=None,
        state=None,
        milestone=milestone_1.id
    )

    _check_summary(summary, 2, 2, 0, 100, 0)

    summary = get_issues_summary(
        Issue.objects.filter(user=user),
        due_date=datetime.now().date(),
        user=user,
        team=None,
        project=None,
        state=None,
        milestone=milestone_2.id
    )

    _check_summary(summary, 2, 2, 0, 300, 0)


def test_resolver(user, client):
    IssueFactory.create_batch(
        5, user=user,
        state=STATE_OPENED,
        total_time_spent=0,
        due_date=datetime.now()
    )
    IssueFactory.create_batch(
        3, user=UserFactory.create(),
        state=STATE_OPENED
    )

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    summary = resolve_issues_summary(
        parent=None,
        info=info,
        user=user.id
    )

    _check_summary(summary, 5, 5, 0, 0, 0)


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


def _check_team_stats(data: IssuesSummary,
                       team: Team,
                       issues_opened_count: int,
                       percentage: float,
                       remains: int):
    stats = next((
        item
        for item in data.teams
        if item.team == team
    ), None)

    assert stats is not None
    assert stats.issues.opened_count == issues_opened_count
    assert stats.issues.percentage == percentage
    assert stats.issues.remains == remains
