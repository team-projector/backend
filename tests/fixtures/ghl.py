import pytest
from django.contrib.auth.models import AnonymousUser
from graphene.test import Client as GQLClient
from graphene_django.rest_framework.tests.test_mutation import mock_info
from graphql import ResolveInfo

from gql import schema
from tests.helpers.ghl_client import GraphQLClient


def _get_mock_info(request):
    """
    Get mock info.

    :param request:
    """
    ret = mock_info()
    ret.context = request
    ret.field_asts = [{}]
    ret.fragments = {}
    return ret


@pytest.fixture()  # delete
def gql_client_authenticated(rf, admin_user):
    """
    Gql client authenticated.

    :param rf:
    :param admin_user:
    """
    request = rf.post("/")
    request.user = admin_user

    return GQLClient(schema, context_value=request)


@pytest.fixture()  # delete
def gql_client_anonymous(rf):
    """
    Gql client anonymous.

    :param rf:
    """
    request = rf.post("/")
    request.user = AnonymousUser()

    return GQLClient(schema, context_value=request)


@pytest.fixture(scope="session")
def ghl_queries():
    """Ghl queries."""
    return schema.get_query_type()


@pytest.fixture(scope="session")
def ghl_mutations():
    """Ghl mutations."""
    return schema.get_mutation_type()


@pytest.fixture()
def ghl_client() -> GraphQLClient:
    """
    Ghl client.

    :rtype: GraphQLClient
    """
    return GraphQLClient()


@pytest.fixture()
def ghl_auth_mock_info(user, auth_rf) -> ResolveInfo:
    """
    Ghl auth mock info.

    :param user:
    :param auth_rf:
    :rtype: ResolveInfo
    """
    request = auth_rf.get("/graphql/")

    return _get_mock_info(request)


@pytest.fixture()
def ghl_mock_info(rf) -> ResolveInfo:
    """
    Ghl mock info.

    :param rf:
    :rtype: ResolveInfo
    """
    request = rf.get("/graphql/")

    return _get_mock_info(request)
