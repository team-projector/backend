# -*- coding: utf-8 -*-

from jnt_django_graphene_toolbox.security.permissions import AllowAny


def test_success(ghl_mock_info):
    """Check if anon user has all permissions."""
    perms = AllowAny()

    assert perms.has_node_permission(info=ghl_mock_info, obj_id="1")
    assert perms.has_mutation_permission(info=ghl_mock_info, root=None)
    assert perms.has_filter_permission(info=ghl_mock_info)
