from datetime import timedelta

import pytest
from django.utils import timezone

from apps.development.models import TeamMember
from tests.test_development.factories import (
    IssueFactory,
    TeamFactory,
    TeamMemberFactory,
)
from tests.test_users.factories import UserFactory


@pytest.fixture()
def team(db):
    """Create team."""
    return TeamFactory.create()


@pytest.fixture()
def leader(user, team):
    """Create team leader."""
    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.LEADER | TeamMember.roles.DEVELOPER,
    )
    return user


@pytest.fixture()
def developer(team):
    """Create developer."""
    user = UserFactory.create()
    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.DEVELOPER,
    )
    return user


@pytest.fixture()
def variables(team):
    """Create variables for check problems."""
    return {
        "team": team.pk,
        "problems": True,
    }


def test_due_date(
    ghl_auth_mock_info,
    issues_summary_query,
    variables,
    leader,
    developer,
):
    """Test due_date issue problems."""
    past_date = timezone.now() - timedelta(weeks=1)
    future_date = timezone.now() + timedelta(weeks=1)

    create_issues(2, author=leader, due_date=None)
    create_issues(3, user=developer, due_date=past_date)
    create_issues(1, user=developer, due_date=future_date, time_estimate=None)

    response = issues_summary_query(
        parent=None,
        info=ghl_auth_mock_info,
        **variables,
    )

    assert response.problems_count == 4


def create_issues(size, **kwargs):
    """Create issues."""
    return IssueFactory.create_batch(size=size, **kwargs)
