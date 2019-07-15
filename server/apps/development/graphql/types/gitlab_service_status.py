import graphene


class GitlabServiceStatusType(graphene.ObjectType):
    name = graphene.String()
    time = graphene.DateTime()
