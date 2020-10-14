import logging
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

from django.utils import timezone
from gitlab.v4 import objects as gl

from apps.development.models import ProjectGroup
from apps.development.services.project_group.gl.provider import (
    ProjectGroupGlProvider,
)

logger = logging.getLogger(__name__)


@dataclass
class _Node:
    group: Optional[gl.Group] = None
    parent: Optional["_Node"] = None
    children: List["_Node"] = field(default_factory=list)

    def get_ancestor(self, ancestor_id: int) -> Optional["_Node"]:
        if not self.parent:
            return None

        if self.parent.group.id == ancestor_id:
            return self.parent

        return self.parent.get_ancestor(ancestor_id)


class _GlGroupForest:
    def __init__(self, gl_groups: List[gl.Group]):
        self.nodes: List[_Node] = self._build_nodes(gl_groups)

    def filter_nodes(self, filter_ids: Iterable[int] = ()) -> List[_Node]:
        filtered = [node for node in self.nodes if node.group.id in filter_ids]
        by_roots = self._get_nodes_by_roots(filter_ids)
        for node in by_roots:
            if node in filtered:
                continue
            filtered.append(node)
        return filtered

    def _get_nodes_by_roots(self, root_ids: Iterable[int]):
        root_ids = set(root_ids)
        filtered_nodes = []

        for node in self.nodes:
            for ancestor_id in root_ids:
                if node.get_ancestor(ancestor_id):
                    filtered_nodes.append(node)
                    break

        return filtered_nodes

    def _build_nodes(self, gl_groups: List[gl.Group]) -> List[_Node]:
        nodes: Dict[int, _Node] = {}
        for group in gl_groups:
            node: _Node = nodes.setdefault(group.id, _Node())
            node.group = group

            if group.parent_id:
                parent_node = nodes.setdefault(group.parent_id, _Node())
                node.parent = parent_node
                parent_node.children.append(node)

        return list(nodes.values())


class ProjectGroupGlManager:
    """Gitlab manager for project groups."""

    def __init__(self):
        """Initializing."""
        self.provider = ProjectGroupGlProvider()

    def sync_groups(self, filter_ids: Iterable[int] = ()) -> None:
        """Sync groups with gitlab."""
        gl_groups = self._get_groups(filter_ids)
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

    def _get_groups(self, filter_ids: Iterable[int] = ()) -> List[gl.Group]:
        gl_groups = self.provider.get_gl_groups(all=True)
        if not filter_ids:
            return gl_groups

        nodes = _GlGroupForest(gl_groups).filter_nodes(filter_ids=filter_ids)
        return [node.group for node in nodes]
