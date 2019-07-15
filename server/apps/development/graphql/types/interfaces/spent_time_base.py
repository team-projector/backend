import graphene

from ..project import ProjectType


class SpentTimeBase(graphene.Interface):
    id = graphene.ID(required=True)
    title = graphene.String()
    gl_id = graphene.Int()
    gl_url = graphene.String()
    gl_last_sync = graphene.DateTime()
    gl_iid = graphene.Int()
    project = graphene.Field(ProjectType)
