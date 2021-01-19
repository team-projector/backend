import pytest
from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied

from apps.development.models import Issue
from apps.users.graphql.resolvers import resolve_user_issues_summary


def test_get_issues_summary_success(user, ghl_auth_mock_info):
    """Test user issues summary empty."""
    issues_summary = resolve_user_issues_summary(user, ghl_auth_mock_info)

    assert not Issue.objects.exists()
    assert not issues_summary.assigned_count
    assert not issues_summary.created_count
    assert not issues_summary.participation_count


def test_get_issues_summary_not_auth(user, ghl_mock_info):
    """Test user issues summary."""
    with pytest.raises(GraphQLPermissionDenied):
        resolve_user_issues_summary(user, ghl_mock_info)
