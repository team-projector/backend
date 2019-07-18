import graphene

from apps.core.graphql.connection_fields import DataSourceConnectionField
from ..label import LabelType
from ..project import ProjectType
from .base import BaseWorkItem


class WorkItem(BaseWorkItem):
    project = graphene.Field(ProjectType)
    labels = DataSourceConnectionField(LabelType)
