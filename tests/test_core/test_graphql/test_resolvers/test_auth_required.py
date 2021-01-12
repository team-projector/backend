import pytest
from django.contrib.auth.models import AnonymousUser
from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied

from apps.core.graphql.resolvers import auth_required


@pytest.fixture()
def inactive_user(user):
    """Make inactive user."""
    user.is_active = False
    user.save()

    return user


def test_auth(ghl_auth_mock_info):
    """Check auth user."""
    assert auth_required(ghl_auth_mock_info) is None


def test_unauth_anonymous(ghl_mock_info):
    """Check auth for anonymous."""
    ghl_mock_info.context.user = AnonymousUser
    with pytest.raises(GraphQLPermissionDenied):
        auth_required(ghl_mock_info)


def test_unauth_not_active(ghl_mock_info, inactive_user):
    """Check unauth for not active."""
    ghl_mock_info.context.user = inactive_user
    with pytest.raises(GraphQLPermissionDenied):
        auth_required(ghl_mock_info)
