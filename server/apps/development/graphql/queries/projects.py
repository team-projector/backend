# -*- coding: utf-8 -*-

import graphene

from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.development.graphql.types import ProjectType


class ProjectsQueries(graphene.ObjectType):
    """Class representing list of available fields for project queries."""

    project = DatasourceRelayNode.Field(ProjectType)
