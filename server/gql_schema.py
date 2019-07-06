import graphene

from apps.development.graphql.query.issues import IssuesQuery


class Query(IssuesQuery,
            graphene.ObjectType):
    pass


schema = graphene.Schema(
    query=Query
)
