# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from django.utils import timezone

from apps.development.models import TeamMember
from apps.development.models.issue import Issue, IssueState
from apps.development.services.issue.summary import get_issues_summary
from tests.test_development.factories import (
    IssueFactory,
    ProjectFactory,
    ProjectMilestoneFactory,
    TeamFactory,
    TeamMemberFactory,
    TicketFactory,
)
from tests.test_development.test_services.test_issues.test_summary.helpers import (  # noqa: E501
    checkers,
)
from tests.test_payroll.factories import IssueSpentTimeFactory
from tests.test_users.factories.user import UserFactory


def test_by_user(user):
    issues = IssueFactory.create_batch(
        5, user=user, state=IssueState.OPENED, due_date=datetime.now()
    )

    another_user = UserFactory.create()
    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=another_user,
        base=IssueFactory.create(user=another_user),
        time_spent=300,
    )

    IssueSpentTimeFactory.create(
        date=datetime.now(), user=user, base=issues[0], time_spent=100
    )

    IssueSpentTimeFactory.create(
        date=datetime.now() - timedelta(days=2),
        user=user,
        base=issues[0],
        time_spent=200,
    )

    summary = get_issues_summary(
        Issue.objects.filter(user=user),
        due_date=datetime.now().date(),
        user=user,
    )

    checkers.check_summary(summary, count=5, opened_count=5, time_spent=100)


def test_by_team(user):
    issues = IssueFactory.create_batch(
        5, user=user, state=IssueState.OPENED, due_date=datetime.now(),
    )

    another_user = UserFactory.create()

    team = TeamFactory.create()
    TeamMemberFactory.create(
        user=user, team=team, roles=TeamMember.roles.LEADER
    )

    TeamMemberFactory.create(
        user=another_user,
        team=TeamFactory.create(),
        roles=TeamMember.roles.DEVELOPER,
    )

    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=another_user,
        base=IssueFactory.create(user=another_user),
        time_spent=300,
    )

    IssueSpentTimeFactory.create(
        date=datetime.now(), user=user, base=issues[0], time_spent=100,
    )

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=2),
        user=user,
        base=issues[0],
        time_spent=200,
    )

    summary = get_issues_summary(
        Issue.objects.filter(user=user),
        due_date=datetime.now().date(),
        user=user,
        team=team,
    )

    checkers.check_summary(summary, count=5, opened_count=5, time_spent=100)


def test_by_project(user):
    projects = ProjectFactory.create_batch(2)

    issues = IssueFactory.create_batch(
        5,
        user=user,
        state=IssueState.OPENED,
        due_date=datetime.now(),
        project=projects[0],
    )

    IssueSpentTimeFactory.create(
        date=datetime.now(), user=user, base=issues[0], time_spent=100,
    )

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=2),
        user=user,
        base=issues[0],
        time_spent=200,
    )

    another_user = UserFactory.create()

    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=another_user,
        base=IssueFactory.create(
            user=another_user,
            state=IssueState.OPENED,
            due_date=datetime.now(),
            project=projects[1],
        ),
        time_spent=300,
    )

    summary = get_issues_summary(
        Issue.objects.filter(user=user),
        due_date=datetime.now().date(),
        user=user,
        project=projects[0],
    )

    checkers.check_summary(summary, count=5, opened_count=5, time_spent=100)

    summary = get_issues_summary(
        Issue.objects.filter(user=another_user),
        due_date=datetime.now().date(),
        user=another_user,
        project=projects[1],
    )

    checkers.check_summary(summary, count=1, opened_count=1, time_spent=300)


def test_by_state(user):
    issue_opened = IssueFactory.create(
        user=user, due_date=datetime.now(), state=IssueState.OPENED
    )

    IssueSpentTimeFactory.create(
        date=datetime.now(), user=user, base=issue_opened, time_spent=100,
    )
    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=2),
        user=user,
        base=issue_opened,
        time_spent=200,
    )

    issue_closed = IssueFactory.create(
        user=user, due_date=datetime.now(), state=IssueState.CLOSED,
    )
    IssueSpentTimeFactory.create(
        date=datetime.now(), user=user, base=issue_closed, time_spent=400,
    )

    summary = get_issues_summary(
        Issue.objects.filter(user=user),
        due_date=datetime.now().date(),
        user=user,
        state=IssueState.OPENED,
    )

    checkers.check_summary(
        summary, count=2, opened_count=1, closed_count=1, time_spent=100
    )

    summary = get_issues_summary(
        Issue.objects.filter(user=user),
        due_date=datetime.now().date(),
        user=user,
        state=IssueState.CLOSED,
    )

    checkers.check_summary(
        summary, count=2, opened_count=1, closed_count=1, time_spent=400,
    )


def test_by_milestone(user):
    milestones = ProjectMilestoneFactory.create_batch(2)
    issues = [
        IssueFactory.create(
            user=user,
            due_date=datetime.now(),
            state=IssueState.OPENED,
            milestone=milestones[0],
        ),
        IssueFactory.create(
            user=user,
            due_date=datetime.now(),
            state=IssueState.OPENED,
            milestone=milestones[1],
        ),
    ]
    IssueSpentTimeFactory.create(
        date=datetime.now(), user=user, base=issues[0], time_spent=100,
    )
    IssueSpentTimeFactory.create(
        date=datetime.now(), user=user, base=issues[1], time_spent=300,
    )

    summary = get_issues_summary(
        Issue.objects.filter(user=user),
        due_date=datetime.now().date(),
        user=user,
        milestone=milestones[0].pk,
    )
    checkers.check_summary(summary, count=2, opened_count=2, time_spent=100)

    summary = get_issues_summary(
        Issue.objects.filter(user=user),
        due_date=datetime.now().date(),
        user=user,
        milestone=milestones[1].pk,
    )
    checkers.check_summary(summary, count=2, opened_count=2, time_spent=300)


def test_by_ticket(user):
    tickets = TicketFactory.create_batch(2)
    issues = [
        IssueFactory.create(
            user=user,
            due_date=datetime.now(),
            state=IssueState.OPENED,
            ticket=tickets[0],
        ),
        IssueFactory.create(
            user=user,
            due_date=datetime.now(),
            state=IssueState.OPENED,
            ticket=tickets[1],
        ),
    ]
    IssueSpentTimeFactory.create(
        date=datetime.now(), user=user, base=issues[0], time_spent=100,
    )
    IssueSpentTimeFactory.create(
        date=datetime.now(), user=user, base=issues[1], time_spent=300,
    )

    IssueFactory.create_batch(
        size=3,
        due_date=datetime.now(),
        state=IssueState.OPENED,
        ticket=TicketFactory.create(),
    )

    summary = get_issues_summary(
        Issue.objects.filter(user=user),
        due_date=datetime.now().date(),
        user=user,
        ticket=tickets[0],
    )
    checkers.check_summary(summary, count=2, opened_count=2, time_spent=100)

    summary = get_issues_summary(
        Issue.objects.filter(user=user),
        due_date=datetime.now().date(),
        user=user,
        ticket=tickets[1].pk,
    )
    checkers.check_summary(summary, count=2, opened_count=2, time_spent=300)
