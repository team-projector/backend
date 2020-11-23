import pytest
from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied
from jnt_django_toolbox.helpers.time import seconds

from apps.development.graphql.types.milestone import MilestoneType
from apps.development.models.project_member import ProjectMember
from tests.test_development.factories import (
    IssueFactory,
    ProjectMemberFactory,
    ProjectMilestoneFactory,
)
from tests.test_development.test_services.test_milestones.helpers import (
    checkers,
)
from tests.test_payroll.factories import IssueSpentTimeFactory


def test_resolver(user, ghl_auth_mock_info):
    """Test resolver."""
    user.customer_hour_rate = 100
    user.hour_rate = 1000
    user.save()

    milestone = ProjectMilestoneFactory.create(budget=10000)
    ProjectMemberFactory.create(
        user=user,
        roles=ProjectMember.roles.MANAGER,
        owner=milestone.owner,
    )

    IssueSpentTimeFactory.create(
        user=user,
        base=IssueFactory.create(user=user, milestone=milestone),
        time_spent=seconds(hours=1),
    )

    checkers.check_milestone_metrics(
        MilestoneType.resolve_metrics(milestone, ghl_auth_mock_info),
        budget=10000,
        payroll=1000,
        profit=9000,
        budget_remains=9900,
        budget_spent=100,
        issues_count=1,
        issues_opened_count=1,
    )


def test_resolver_not_manager(user, ghl_auth_mock_info):
    """Test resolver without permissions."""
    milestone = ProjectMilestoneFactory.create(budget=10000)
    ProjectMemberFactory.create(
        user=user,
        roles=ProjectMember.roles.DEVELOPER,
        owner=milestone.owner,
    )

    with pytest.raises(GraphQLPermissionDenied):
        MilestoneType.resolve_metrics(milestone, ghl_auth_mock_info)
