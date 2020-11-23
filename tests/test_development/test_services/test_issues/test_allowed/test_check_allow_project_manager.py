import pytest
from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied

from apps.development.services.issue.allowed import check_allow_project_manager
from apps.users.models import User


@pytest.mark.parametrize(
    "roles",
    [
        User.roles.MANAGER,
        User.roles.DEVELOPER | User.roles.MANAGER,
        User.roles.TEAM_LEADER | User.roles.MANAGER,
        User.roles.TEAM_LEADER | User.roles.DEVELOPER | User.roles.MANAGER,
        User.roles.CUSTOMER | User.roles.SHAREHOLDER | User.roles.MANAGER,
    ],
)
def test_allow(user, roles):
    """Test user roles is Manager."""
    User.objects.filter(id=user.pk).update(roles=roles)
    user.refresh_from_db()
    assert check_allow_project_manager(user) is None


@pytest.mark.parametrize(
    "roles",
    [
        User.roles.DEVELOPER,
        User.roles.TEAM_LEADER,
        User.roles.CUSTOMER,
        User.roles.SHAREHOLDER,
        User.roles.CUSTOMER | User.roles.SHAREHOLDER,
    ],
)
def test_not_allow_user(user, roles):
    """Test user role not manager."""
    User.objects.filter(id=user.pk).update(roles=roles)
    user.refresh_from_db()
    with pytest.raises(GraphQLPermissionDenied):
        check_allow_project_manager(user)
