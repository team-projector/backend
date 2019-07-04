import graphene
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField

from apps.development.graphql.nodes.issues import IssueNode


class Query(graphene.ObjectType):
    issue = relay.Node.Field(IssueNode)
    issues = DjangoFilterConnectionField(IssueNode)


schema = graphene.Schema(
    query=Query
)
