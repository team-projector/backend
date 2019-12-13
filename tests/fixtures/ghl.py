# -*- coding: utf-8 -*-

import pytest
from django.contrib.auth.models import AnonymousUser
from graphene.test import Client as GQLClient
from graphene_django.rest_framework.tests.test_mutation import mock_info
from graphql import ResolveInfo

from gql import schema
from tests.helpers.ghl_client import GraphQLClient


@pytest.fixture()  # delete
def gql_client_authenticated(rf, admin_user):
    request = rf.post('/')
    request.user = admin_user

    return GQLClient(schema, context=request)


@pytest.fixture()  # delete
def gql_client_anonymous(rf):
    request = rf.post('/')
    request.user = AnonymousUser()

    return GQLClient(schema, context=request)


@pytest.fixture(scope='session')
def ghl_queries():
    return schema.get_query_type()


@pytest.fixture(scope='session')
def ghl_mutations():
    return schema.get_mutation_type()


@pytest.fixture()  # type: ignore
def ghl_client() -> GraphQLClient:
    return GraphQLClient()


@pytest.fixture()  # type: ignore
def ghl_auth_mock_info(user, rf) -> ResolveInfo:
    rf.set_user(user)
    request = rf.get('/graphql/')

    resolve_info = mock_info()
    resolve_info.context = request

    return resolve_info


@pytest.fixture()  # type: ignore
def ghl_mock_info(user, rf) -> ResolveInfo:
    request = rf.get('/graphql/')

    resolve_info = mock_info()
    resolve_info.context = request

    return resolve_info
