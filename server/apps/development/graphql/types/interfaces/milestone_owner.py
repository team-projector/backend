import graphene


class MilestoneOwner(graphene.Interface):
    id = graphene.ID(required=True)
    title = graphene.String()
    full_title = graphene.String()
    gl_id = graphene.Int()
    gl_url = graphene.String()
    gl_last_sync = graphene.DateTime()
    gl_avatar = graphene.String()
