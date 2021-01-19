import graphene

from apps.development.graphql.fields import LabelsConnectionField
from apps.users.graphql.types import UserType


class WorkItem(graphene.Interface):
    """Work item interface."""

    id = graphene.ID(required=True)  # noqa: WPS125
    title = graphene.String()
    gl_id = graphene.Int()
    gl_url = graphene.String()
    gl_last_sync = graphene.DateTime()
    gl_iid = graphene.Int()
    project = graphene.Field("apps.development.graphql.types.ProjectType")
    labels = LabelsConnectionField()
    user = graphene.Field(UserType)
