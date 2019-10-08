# -*- coding: utf-8 -*-

import logging
from typing import Optional

from gitlab.v4.objects import Group as GlGroup

from apps.core.gitlab import get_gitlab_client

from ...models import ProjectGroup

logger = logging.getLogger(__name__)


def load_groups() -> None:
    """Load all groups."""
    gl = get_gitlab_client()
    gl_groups = gl.groups.list(all=True)
    gl_groups_map = {
        item.id: item
        for item in gl_groups
    }

    while gl_groups:
        _load_group(gl_groups[0], gl_groups, gl_groups_map)


def _load_group(
    gl_group: GlGroup,
    gl_groups: GlGroup,
    gl_groups_map: dict,
) -> ProjectGroup:
    parent = None

    if gl_group.parent_id:
        parent = ProjectGroup.objects.filter(
            gl_id=gl_group.parent_id,
        ).first()
        if not parent and gl_group.parent_id in gl_groups_map:
            parent = _load_group(
                gl_groups_map[gl_group.parent_id], gl_groups, gl_groups_map,
            )

    gl_groups.remove(gl_group)

    return load_single_group(gl_group, parent)


def load_single_group(
    gl_group: GlGroup,
    parent: Optional[ProjectGroup],
) -> ProjectGroup:
    """Load group."""
    group, _ = ProjectGroup.objects.sync_gitlab(
        gl_id=gl_group.id,
        gl_url=gl_group.web_url,
        gl_avatar=gl_group.avatar_url,
        parent=parent,
        title=gl_group.name,
        full_title=gl_group.full_name,
    )

    logger.info(f'Group "{group}" is synced')

    return group
