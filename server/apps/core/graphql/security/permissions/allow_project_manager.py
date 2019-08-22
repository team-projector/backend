from typing import Any

from graphql import ResolveInfo


class AllowProjectManager:
    """
    Allow performing action only for project manager.
    """

    @staticmethod
    def has_node_permission(info: ResolveInfo,
                            id: str) -> bool:
        return info.context.user.roles.project_manager

    @staticmethod
    def has_mutation_permission(root: Any,
                                info: ResolveInfo,
                                **kwargs) -> bool:
        return info.context.user.roles.project_manager

    @staticmethod
    def has_filter_permission(info: ResolveInfo) -> bool:
        return info.context.user.roles.project_manager
