import graphene

from apps.development.models.issue import IssueState as ModelIssueState

IssueState = graphene.Enum.from_enum(ModelIssueState)
