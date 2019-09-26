# -*- coding: utf-8 -*-

import graphene

from apps.core.graphql.connection_fields import DataSourceConnectionField

from ..label import LabelType
from ..project import ProjectType


class WorkItem(graphene.Interface):
    id = graphene.ID(required=True)
    title = graphene.String()
    gl_id = graphene.Int()
    gl_url = graphene.String()
    gl_last_sync = graphene.DateTime()
    gl_iid = graphene.Int()
    project = graphene.Field(ProjectType)
    labels = DataSourceConnectionField(LabelType)
