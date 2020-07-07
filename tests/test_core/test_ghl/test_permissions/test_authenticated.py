# -*- coding: utf-8 -*-

from jnt_django_graphene_toolbox.security.permissions import AllowAuthenticated


def test_success(ghl_auth_mock_info):
    """Check if anon user has all permissions."""
    perms = AllowAuthenticated()

    assert perms.has_node_permission(info=ghl_auth_mock_info, obj_id="1")
    assert perms.has_mutation_permission(info=ghl_auth_mock_info, root=None)
    assert perms.has_filter_permission(info=ghl_auth_mock_info)


def test_unauth(ghl_mock_info):
    """Check if anon user has"t permissions."""
    perms = AllowAuthenticated()

    assert not perms.has_node_permission(info=ghl_mock_info, obj_id="1")
    assert not perms.has_mutation_permission(info=ghl_mock_info, root=None)
    assert not perms.has_filter_permission(info=ghl_mock_info)
