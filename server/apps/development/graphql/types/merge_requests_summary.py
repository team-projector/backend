import graphene


class MergeRequestsSummaryType(graphene.ObjectType):
    count = graphene.Int()
    opened_count = graphene.Int()
    closed_count = graphene.Int()
    merged_count = graphene.Int()