from django.contrib.auth.models import AnonymousUser
from tests.test_development.factories import IssueFactory
from tests.test_development.factories_gitlab import AttrDict

from apps.core.graphql.security.permissions import (
    AllowAny,
    AllowAuthenticated,
    AllowProjectManager,
)
from apps.development.graphql.types.issue import IssueType


def test_any(client):
    client.user = AnonymousUser()
    info = AttrDict({'context': client})

    perms = AllowAny()
    assert perms.has_node_permission(info=info, obj_id='1') is True
    assert perms.has_mutation_permission(root=None, info=info) is True
    assert perms.has_filter_permission(info=info) is True


def test_authenticated(client, user):
    client.user = AnonymousUser()
    info = AttrDict({'context': client})

    perms = AllowAuthenticated()
    assert perms.has_node_permission(info=info, obj_id='1') is False
    assert perms.has_mutation_permission(root=None, info=info) is False
    assert perms.has_filter_permission(info=info) is False

    client.user = user

    assert perms.has_node_permission(info=info, obj_id='1') is True
    assert perms.has_mutation_permission(root=None, info=info) is True
    assert perms.has_filter_permission(info=info) is True


def test_project_manager(client, user):
    client.user = user
    info = AttrDict({'context': client})

    perms = AllowProjectManager()
    assert bool(perms.has_node_permission(info=info, obj_id='1')) is False
    assert bool(perms.has_mutation_permission(root=None, info=info)) is False
    assert bool(perms.has_filter_permission(info=info)) is False

    user.roles.PROJECT_MANAGER = True
    user.save()

    assert bool(perms.has_node_permission(info=info, obj_id='1')) is True
    assert bool(perms.has_mutation_permission(root=None, info=info)) is True
    assert bool(perms.has_filter_permission(info=info)) is True


def test_auth_node(client, user):
    issue = IssueFactory.create(user=user)

    client.user = AnonymousUser()

    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    assert IssueType().get_node(info, issue.id) is None

    client.user = user

    assert IssueType().get_node(info, issue.id) == issue
