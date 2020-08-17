# -*- coding: utf-8 -*-

from datetime import datetime

from apps.development.models import TeamMember
from apps.development.models.issue import Issue
from apps.development.services.issue.summary import (
    get_issues_summary,
    get_team_summaries,
)
from tests.test_development.factories import (
    IssueFactory,
    TeamFactory,
    TeamMemberFactory,
)
from tests.test_development.test_services.test_issues.test_summary.helpers import (  # noqa: E501
    checkers,
)
from tests.test_users.factories.user import UserFactory


def test_team_summary(db):
    """
    Test team summary.

    :param db:
    """
    users = UserFactory.create_batch(2)
    teams = TeamFactory.create_batch(2)
    TeamMemberFactory.create(
        user=users[0], team=teams[0], roles=TeamMember.roles.DEVELOPER,
    )
    IssueFactory.create_batch(
        5,
        user=users[0],
        total_time_spent=300,
        time_estimate=400,
        due_date=datetime.now().date(),
    )

    TeamMemberFactory.create(
        user=users[1], team=teams[1], roles=TeamMember.roles.DEVELOPER,
    )
    IssueFactory.create_batch(
        3,
        user=users[1],
        total_time_spent=100,
        time_estimate=400,
        due_date=datetime.now().date(),
    )

    summary = get_issues_summary(Issue.objects.all())
    summary.teams = get_team_summaries(summary.queryset)

    assert len(summary.teams) == 2
    checkers.check_team_stats(
        summary,
        teams[0],
        issues_opened_count=5,
        percentage=5 / 8,
        remains=500,
    )
    checkers.check_team_stats(
        summary,
        teams[1],
        issues_opened_count=3,
        percentage=3 / 8,
        remains=900,
    )
