import graphene
from django.contrib.auth.mixins import LoginRequiredMixin
from graphene_django.views import GraphQLView

from apps.development.graphql.query.issues import IssuesQuery


class PrivateGraphQLView(LoginRequiredMixin,
                         GraphQLView):
    pass


class Query(IssuesQuery,
            graphene.ObjectType):
    pass


schema = graphene.Schema(
    query=Query
)
