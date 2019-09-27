# -*- coding: utf-8 -*-

from datetime import datetime

from apps.core.graphql.connection_fields import DataSourceConnectionField
from apps.core.graphql.connections import DataSourceConnection
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.core.graphql.types import BaseDjangoObjectType
from apps.development.graphql.filters import MilestonesFilterSet
from apps.development.graphql.resolvers import ProjectMilestonesResolver
from apps.development.graphql.types.interfaces import MilestoneOwner
from apps.development.graphql.types.milestone import MilestoneType
from apps.development.models import Project
from apps.development.services.summary.issues import IssuesProjectSummary


class ProjectType(BaseDjangoObjectType):
    milestones = DataSourceConnectionField(
        MilestoneType,
        filterset_class=MilestonesFilterSet,
    )

    def resolve_milestones(self: Project, info, **kwargs):
        if isinstance(getattr(self, 'parent_type', None), IssuesProjectSummary):
            ret = self.active_milestones

            if kwargs.get('order_by') == 'due_date':
                default = datetime.max.date()
                ret = sorted(ret, key=lambda item: item.due_date or default)

            elif kwargs.get('order_by') == '-due_date':
                default = datetime.min.date()
                ret = sorted(ret, key=lambda item: item.due_date or default,
                             reverse=True)

            return ret

        resolver = ProjectMilestonesResolver(self, info, **kwargs)

        return resolver.execute()

    class Meta:
        model = Project
        interfaces = (DatasourceRelayNode, MilestoneOwner)
        connection_class = DataSourceConnection
        name = 'Project'
