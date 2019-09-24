from graphql.language.ast import Field, Name, SelectionSet
from django.db import connection
from django.test import override_settings

from apps.development.graphql.types.issue import IssueType
from apps.development.models import Issue
from tests.test_development.factories import IssueFactory
from tests.test_development.factories_gitlab import AttrDict


@override_settings(DEBUG=True)
def test_select_related_user(user, client):
    IssueFactory.create(user=user)

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    query_count_before = len(connection.queries)

    issues = IssueType().get_queryset(
        Issue.objects.all(), info
    )

    assert issues.first().user == user

    query_count_after = len(connection.queries)
    assert query_count_after - query_count_before == 3

    user_field = _create_field('user')
    node = _create_field('node', user_field)
    edges = _create_field('edges', node)
    info.field_asts = [_create_field('allIssues', edges)]

    query_count_before = len(connection.queries)

    issues = IssueType().get_queryset(
        Issue.objects.all(), info
    )

    assert issues.first().user == user

    query_count_after = len(connection.queries)
    assert query_count_after - query_count_before == 2


def _create_field(name, selection=None):
    field = Field(name=Name(value=name))

    if selection:
        field.selection_set = SelectionSet(selections=[selection])

    return field
