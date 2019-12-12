from django.db import connection
from django.test import override_settings
from graphql.language.ast import Field, Name, SelectionSet
from tests.test_development.factories import MergeRequestFactory
from tests.test_development.factories_gitlab import AttrDict

from apps.development.graphql.types.merge_request import MergeRequestType
from apps.development.models import MergeRequest


@override_settings(DEBUG=True)
def test_select_related_user(user, client):
    MergeRequestFactory.create(user=user)

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    query_count_before = len(connection.queries)

    merge_requests = MergeRequestType().get_queryset(
        MergeRequest.objects.all(), info
    )

    assert merge_requests.first().user == user

    query_count_after = len(connection.queries)
    assert query_count_after - query_count_before == 3

    user_field = _create_field('user')
    node = _create_field('node', user_field)
    edges = _create_field('edges', node)
    info.field_asts = [_create_field('allMergeRequests', edges)]

    query_count_before = len(connection.queries)

    merge_requests = MergeRequestType().get_queryset(
        MergeRequest.objects.all(), info
    )

    assert merge_requests.first().user == user

    query_count_after = len(connection.queries)
    assert query_count_after - query_count_before == 2


def _create_field(name, selection=None):
    field = Field(name=Name(value=name))

    if selection:
        field.selection_set = SelectionSet(selections=[selection])

    return field
