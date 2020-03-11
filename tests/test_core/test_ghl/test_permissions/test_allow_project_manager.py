# -*- coding: utf-8 -*-

from apps.core.graphql.security.permissions import AllowProjectManager


def test_success(user, ghl_auth_mock_info):
    """Check if project manager user has permissions."""
    perms = AllowProjectManager()

    user.roles.PROJECT_MANAGER = True
    user.save()

    assert perms.has_node_permission(info=ghl_auth_mock_info, obj_id="1")
    assert perms.has_mutation_permission(info=ghl_auth_mock_info, root=None)
    assert perms.has_filter_permission(info=ghl_auth_mock_info)


def test_unauth(ghl_mock_info):
    """Check if anon user has"t permissions."""
    perms = AllowProjectManager()

    assert not perms.has_node_permission(info=ghl_mock_info, obj_id="1")
    assert not perms.has_mutation_permission(info=ghl_mock_info, root=None)
    assert not perms.has_filter_permission(info=ghl_mock_info)


def test_not_project_manager(ghl_auth_mock_info):
    """Check if not project manager user has"t permissions."""
    perms = AllowProjectManager()

    assert not perms.has_node_permission(info=ghl_auth_mock_info, obj_id="1")
    assert not perms.has_mutation_permission(
        info=ghl_auth_mock_info, root=None
    )
    assert not perms.has_filter_permission(info=ghl_auth_mock_info)
