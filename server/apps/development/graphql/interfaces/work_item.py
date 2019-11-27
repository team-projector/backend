# -*- coding: utf-8 -*-

import graphene

from apps.core.graphql.connection_fields import DataSourceConnectionField
from apps.development.graphql.types.label import LabelType
from apps.development.graphql.types.project import ProjectType
from apps.users.graphql.types import UserType


class WorkItem(graphene.Interface):
    """Work item interface."""

    id = graphene.ID(required=True)  # noqa A003
    title = graphene.String()
    gl_id = graphene.Int()
    gl_url = graphene.String()
    gl_last_sync = graphene.DateTime()
    gl_iid = graphene.Int()
    project = graphene.Field(ProjectType)
    labels = DataSourceConnectionField(LabelType)
    state = graphene.String()
    user = graphene.Field(UserType)

    def resolve_state(self, info, **kwargs):  # noqa WPS110
        """Get work item state."""
        if self.state:
            return self.state.upper()

        return None
