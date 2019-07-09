import graphene
from graphene_django import DjangoObjectType

from apps.development.models import Issue
from apps.development.services.metrics.issue import get_issue_metrcis
from apps.development.services.problems.issue import get_issue_problems
from .issue_metrics import IssueMetrics


class IssueType(DjangoObjectType):
    class Meta:
        model = Issue

    metrics = graphene.Field(IssueMetrics)
    problems = graphene.List(graphene.String)

    def resolve_problems(self, info, **kwargs):
        return get_issue_problems(self)

    def resolve_metrics(self, info, **kwargs):
        return get_issue_metrcis(self)
