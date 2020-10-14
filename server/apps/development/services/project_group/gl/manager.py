import logging
from typing import Dict, Iterable, List, Optional

from django.utils import timezone
from gitlab.v4 import objects as gl

from apps.development.models import ProjectGroup
from apps.development.services.project_group.gl.provider import (
    ProjectGroupGlProvider,
)

logger = logging.getLogger(__name__)


class ProjectGroupGlManager:
    """Gitlab manager for project groups."""

    def __init__(self):
        """Initializing."""
        self.provider = ProjectGroupGlProvider()

    def sync_groups(self, filter_ids: Iterable[int] = ()) -> None:
        """Sync groups with gitlab."""
        gl_groups = self.provider.get_gl_groups(all=True)
        if filter_ids:
            gl_groups = [
                group for group in gl_groups if group.id in filter_ids
            ]
        gl_groups_map = {gl_group.id: gl_group for gl_group in gl_groups}

        while gl_groups:
            self.sync_group(
                gl_groups[0],
                gl_groups,
                gl_groups_map,
            )

    def sync_group(
        self,
        gl_group: gl.Group,
        gl_groups: List[gl.Group],
        gl_groups_map: Dict[int, gl.Group],
    ) -> ProjectGroup:
        """Sync group with gitlab."""
        parent = None

        if gl_group.parent_id:
            parent = ProjectGroup.objects.filter(
                gl_id=gl_group.parent_id,
            ).first()

            if not parent and gl_group.parent_id in gl_groups_map:
                parent = self.sync_group(
                    gl_groups_map[gl_group.parent_id],
                    gl_groups,
                    gl_groups_map,
                )

        gl_groups.remove(gl_group)

        return self.update_group(gl_group, parent)

    def update_group(
        self,
        gl_group: gl.Group,
        parent: Optional[ProjectGroup],
    ) -> ProjectGroup:
        """Update project group data based on gitlab."""
        fields = {
            "gl_url": gl_group.web_url or "",
            "gl_avatar": gl_group.avatar_url or "",
            "parent": parent,
            "title": gl_group.name,
            "full_title": gl_group.full_name,
            "gl_last_sync": timezone.now(),
        }
        group, _ = ProjectGroup.objects.update_or_create(
            gl_id=gl_group.id,
            defaults=fields,
        )

        logger.info("Group '{0}' is synced".format(group))

        return group
