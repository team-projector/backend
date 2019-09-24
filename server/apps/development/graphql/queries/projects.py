# -*- coding: utf-8 -*-

import graphene

from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.development.graphql.types import ProjectType


class ProjectsQueries(graphene.ObjectType):
    project = DatasourceRelayNode.Field(ProjectType)
