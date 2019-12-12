from datetime import datetime, timedelta

from django.utils import timezone

from apps.development.graphql.resolvers import resolve_issues_summary
from apps.development.graphql.resolvers.issues_summary import (
    resolve_issues_project_summaries,
    resolve_issues_team_summaries,
)
from apps.development.models import Project, Team, TeamMember
from apps.development.models.issue import ISSUE_STATES, Issue
from apps.development.models.milestone import MILESTONE_STATES
from apps.development.services import issue as issue_service
from tests.test_development.factories import (
    IssueFactory,
    ProjectFactory,
    ProjectGroupFactory,
    ProjectMilestoneFactory,
    TeamFactory,
    TeamMemberFactory,
    TicketFactory,
)
from tests.test_development.factories_gitlab import AttrDict
from tests.test_payroll.factories import IssueSpentTimeFactory
from tests.test_users.factories.user import UserFactory


def test_issue_counts(user):
    IssueFactory.create_batch(
        5, user=user,
        state=ISSUE_STATES.OPENED,
        total_time_spent=0,
        due_date=datetime.now()
    )
    IssueFactory.create_batch(
        3, user=user,
        state=ISSUE_STATES.CLOSED,
        total_time_spent=0,
        due_date=datetime.now()
    )

    summary = issue_service.get_issues_summary(
        Issue.objects.filter(user=user),
        user=user,
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

    summary = issue_service.get_issues_summary(
        Issue.objects.filter(user=user),
        user=user,
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

    summary = issue_service.get_issues_summary(
        Issue.objects.filter(user=user),
        due_date=datetime.now().date(),
        user=user,
    )

    summary.projects = issue_service.get_project_summaries(summary.queryset)

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
        roles=TeamMember.roles.DEVELOPER
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
        roles=TeamMember.roles.DEVELOPER
    )
    IssueFactory.create_batch(
        3,
        user=user_2,
        total_time_spent=100,
        time_estimate=400,
        due_date=datetime.now().date()
    )

    summary = issue_service.get_issues_summary(
        Issue.objects.all(),
    )

    summary.teams = issue_service.get_team_summaries(summary.queryset)

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
        m = ProjectMilestoneFactory(state=MILESTONE_STATES.ACTIVE)
        ProjectMilestoneFactory(
            owner=m.owner,
            due_date=timezone.now() - timezone.timedelta(days=n),
        )
        ProjectMilestoneFactory(
            owner=m.owner,
            due_date=timezone.now() + timezone.timedelta(days=n),
            state=MILESTONE_STATES.ACTIVE
        )

        projs.append(m.owner)

    results = sorted(projs, key=issue_service.get_min_due_date)
    assert [projs[0].id, projs[1].id, projs[2].id] == [p.id for p in results]


def test_sort_projects_by_milestone_neested(db):
    projs = []
    for n in range(3):
        group = ProjectGroupFactory(parent=ProjectGroupFactory())
        proj = ProjectFactory(group=group)

        ProjectMilestoneFactory(state=MILESTONE_STATES.ACTIVE)
        ProjectMilestoneFactory(
            owner=group.parent,
            due_date=timezone.now() - timezone.timedelta(days=n),
            state=MILESTONE_STATES.ACTIVE
        )
        ProjectMilestoneFactory(
            owner=group.parent,
            due_date=timezone.now() + timezone.timedelta(days=n),
            state=MILESTONE_STATES.ACTIVE
        )

        projs.append(proj)

    results = sorted(projs, key=issue_service.get_min_due_date)
    assert [projs[2].id, projs[1].id, projs[0].id] == [p.id for p in results]


def test_time_spents_by_user(user):
    issues = IssueFactory.create_batch(
        5, user=user,
        state=ISSUE_STATES.OPENED,
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

    summary = issue_service.get_issues_summary(
        Issue.objects.filter(user=user),
        due_date=datetime.now().date(),
        user=user,
    )

    _check_summary(summary, 5, 5, 0, 100, 0)


def test_time_spents_by_team(user):
    issues = IssueFactory.create_batch(
        5, user=user,
        state=ISSUE_STATES.OPENED,
        due_date=datetime.now()
    )

    another_user = UserFactory.create()

    team = TeamFactory.create()
    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.LEADER
    )

    TeamMemberFactory.create(
        user=another_user,
        team=TeamFactory.create(),
        roles=TeamMember.roles.DEVELOPER
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

    summary = issue_service.get_issues_summary(
        Issue.objects.filter(user=user),
        due_date=datetime.now().date(),
        user=user,
        team=team,
    )

    _check_summary(summary, 5, 5, 0, 100, 0)


def test_time_spents_by_project(user):
    project_1 = ProjectFactory()
    project_2 = ProjectFactory()

    issues = IssueFactory.create_batch(
        5, user=user,
        state=ISSUE_STATES.OPENED,
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
        state=ISSUE_STATES.OPENED,
        due_date=datetime.now(),
        project=project_2
    )

    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=another_user,
        base=issue_another_user,
        time_spent=300
    )

    summary = issue_service.get_issues_summary(
        Issue.objects.filter(user=user),
        due_date=datetime.now().date(),
        user=user,
        project=project_1,
    )

    _check_summary(summary, 5, 5, 0, 100, 0)

    summary = issue_service.get_issues_summary(
        Issue.objects.filter(user=another_user),
        due_date=datetime.now().date(),
        user=another_user,
        project=project_2,
    )

    _check_summary(summary, 1, 1, 0, 300, 0)


def test_time_spents_by_state(user):
    issue_opened = IssueFactory.create(
        user=user,
        due_date=datetime.now(),
        state=ISSUE_STATES.OPENED
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
        state=ISSUE_STATES.CLOSED
    )

    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=user,
        base=issue_closed,
        time_spent=400
    )

    summary = issue_service.get_issues_summary(
        Issue.objects.filter(user=user),
        due_date=datetime.now().date(),
        user=user,
        state=ISSUE_STATES.OPENED,
    )

    _check_summary(summary, 2, 1, 1, 100, 0)

    summary = issue_service.get_issues_summary(
        Issue.objects.filter(user=user),
        due_date=datetime.now().date(),
        user=user,
        state=ISSUE_STATES.CLOSED,
    )

    _check_summary(summary, 2, 1, 1, 400, 0)


def test_time_spents_by_milestone(user):
    milestone_1 = ProjectMilestoneFactory.create()
    issue_1 = IssueFactory.create(
        user=user,
        due_date=datetime.now(),
        state=ISSUE_STATES.OPENED,
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
        state=ISSUE_STATES.OPENED,
        milestone=milestone_2
    )
    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=user,
        base=issue_2,
        time_spent=300
    )

    summary = issue_service.get_issues_summary(
        Issue.objects.filter(user=user),
        due_date=datetime.now().date(),
        user=user,
        milestone=milestone_1.id
    )

    _check_summary(summary, 2, 2, 0, 100, 0)

    summary = issue_service.get_issues_summary(
        Issue.objects.filter(user=user),
        due_date=datetime.now().date(),
        user=user,
        milestone=milestone_2.id
    )

    _check_summary(summary, 2, 2, 0, 300, 0)


def test_time_spents_by_ticket(user):
    ticket_1 = TicketFactory.create()
    issue_1 = IssueFactory.create(
        user=user,
        due_date=datetime.now(),
        state=ISSUE_STATES.OPENED,
        ticket=ticket_1,
    )
    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=user,
        base=issue_1,
        time_spent=100
    )

    ticket_2 = TicketFactory.create()
    issue_2 = IssueFactory.create(
        user=user,
        due_date=datetime.now(),
        state=ISSUE_STATES.OPENED,
        ticket=ticket_2
    )
    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=user,
        base=issue_2,
        time_spent=300
    )

    IssueFactory.create_batch(
        size=3,
        due_date=datetime.now(),
        state=ISSUE_STATES.OPENED,
        ticket=TicketFactory.create()
    )

    summary = issue_service.get_issues_summary(
        Issue.objects.filter(user=user),
        due_date=datetime.now().date(),
        user=user,
        ticket=ticket_1
    )

    _check_summary(summary, 2, 2, 0, 100, 0)

    summary = issue_service.get_issues_summary(
        Issue.objects.filter(user=user),
        due_date=datetime.now().date(),
        user=user,
        ticket=ticket_2.id
    )

    _check_summary(summary, 2, 2, 0, 300, 0)


def test_resolve_issues_summary(user, client):
    IssueFactory.create_batch(
        5, user=user,
        state=ISSUE_STATES.OPENED,
        total_time_spent=0,
        due_date=datetime.now()
    )
    IssueFactory.create_batch(
        3, user=UserFactory.create(),
        state=ISSUE_STATES.OPENED
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


def test_resolve_issues_project_summaries(user):
    project = ProjectFactory()

    IssueFactory.create_batch(
        5,
        user=user,
        total_time_spent=300,
        time_estimate=400,
        project=project,
        due_date=datetime.now().date()
    )

    parent = AttrDict({
        'queryset': Issue.objects.all()
    })

    issues = resolve_issues_project_summaries(parent, None)[0].issues

    assert issues.opened_count == 5
    assert issues.percentage == 1.0
    assert issues.remains == 500


def test_resolve_issues_team_summaries(user):
    team = TeamFactory.create()
    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.DEVELOPER
    )
    IssueFactory.create_batch(
        5,
        user=user,
        total_time_spent=300,
        time_estimate=400,
        due_date=datetime.now().date()
    )

    parent = AttrDict({
        'queryset': Issue.objects.all()
    })

    issues = resolve_issues_team_summaries(parent, None)[0].issues

    assert issues.opened_count == 5
    assert issues.percentage == 1.0
    assert issues.remains == 500


def _check_summary(data: issue_service.IssuesSummary,
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


def _check_project_stats(data: issue_service.IssuesSummary,
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


def _check_team_stats(data: issue_service.IssuesSummary,
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
