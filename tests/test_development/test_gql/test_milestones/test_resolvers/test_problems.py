from datetime import datetime, timedelta

import pytest
from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied

from apps.development.graphql.types.milestone import MilestoneType
from apps.development.models.milestone import MilestoneState
from apps.development.models.project_member import ProjectMember
from apps.development.services.milestone.problems import PROBLEM_OVER_DUE_DAY
from tests.test_development.factories import (
    ProjectMemberFactory,
    ProjectMilestoneFactory,
)


def test_resolver(user, ghl_auth_mock_info):
    """
    Test resolver.

    :param db:
    """
    problem_milestone = ProjectMilestoneFactory.create(
        state=MilestoneState.ACTIVE,
        due_date=datetime.now().date() - timedelta(days=1),
    )

    ProjectMemberFactory.create(
        user=user,
        roles=ProjectMember.roles.MANAGER,
        owner=problem_milestone.owner,
    )

    problems = MilestoneType.resolve_problems(
        problem_milestone,
        ghl_auth_mock_info,
    )
    assert problems == [PROBLEM_OVER_DUE_DAY]


def test_resolver_not_manager(user, ghl_auth_mock_info):
    """Test resolver without permissions."""
    milestone = ProjectMilestoneFactory.create(budget=10000)
    ProjectMemberFactory.create(
        user=user,
        roles=ProjectMember.roles.DEVELOPER,
        owner=milestone.owner,
    )

    with pytest.raises(GraphQLPermissionDenied):
        MilestoneType.resolve_problems(milestone, ghl_auth_mock_info)
