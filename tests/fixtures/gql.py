import pytest
from graphene.test import Client as GQLClient

from gql import schema
from tests.helpers.gql_client import GraphQLClient
from tests.helpers.gql_raw_query_provider import GhlRawQueryProvider


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


@pytest.fixture(scope="session")
def ghl_queries():
    """Ghl queries."""
    return schema.get_query_type()


@pytest.fixture(scope="session")
def ghl_mutations():
    """Ghl mutations."""
    return schema.get_mutation_type()


@pytest.fixture()
def gql_client() -> GraphQLClient:
    """
    Ghl client.

    :rtype: GraphQLClient
    """
    return GraphQLClient()


@pytest.fixture()
def ghl_raw(request) -> GhlRawQueryProvider:
    """Ghl raw query provider."""
    return GhlRawQueryProvider(request.fspath.dirname)
