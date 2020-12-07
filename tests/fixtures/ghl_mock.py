import pytest
from graphene_django.rest_framework.tests.test_mutation import mock_info
from graphql import ResolveInfo


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
