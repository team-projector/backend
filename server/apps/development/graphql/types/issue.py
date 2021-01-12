import graphene
from django.db.models import QuerySet
from jnt_django_graphene_toolbox.helpers.selected_fields import (
    is_field_selected,
)
from jnt_django_graphene_toolbox.nodes import ModelRelayNode
from jnt_django_graphene_toolbox.types import BaseModelObjectType

from apps.development.graphql import fields, interfaces
from apps.development.graphql.types import IssueMetricsType
from apps.development.graphql.types.enums import IssueState
from apps.development.models import Issue
from apps.development.services.issue import allowed, metrics
from apps.development.services.issue.problems import get_issue_problems
from apps.users.graphql.fields import UsersConnectionField


class IssueType(BaseModelObjectType):
    """Issue type."""

    class Meta:
        model = Issue
        interfaces = (ModelRelayNode, interfaces.WorkItem)
        auth_required = True

    metrics = graphene.Field(IssueMetricsType)
    problems = graphene.List(graphene.String)
    time_spent = graphene.Field(graphene.Int)
    author = graphene.Field("apps.users.graphql.types.UserType")
    participants = UsersConnectionField()
    gl_url = graphene.String()
    gl_last_sync = graphene.DateTime()
    title = graphene.String()
    description = graphene.String()
    time_estimate = graphene.Int()
    total_time_spent = graphene.Int()
    state = graphene.Field(IssueState)
    created_at = graphene.DateTime()
    updated_at = graphene.DateTime()
    closed_at = graphene.DateTime()
    due_date = graphene.Date()
    is_merged = graphene.Boolean()
    labels = fields.LabelsConnectionField()
    project = graphene.Field("apps.development.graphql.types.ProjectType")
    user = graphene.Field("apps.users.graphql.types.UserType")
    milestone = graphene.Field("apps.development.graphql.types.MilestoneType")
    ticket = graphene.Field("apps.development.graphql.types.TicketType")
    merge_requests = fields.MergeRequestsConnectionField()

    @classmethod
    def get_queryset(cls, queryset, info) -> QuerySet:  # noqa: WPS110
        """Get issues."""
        if isinstance(queryset, list):
            return queryset

        queryset = allowed.filter_allowed_for_user(queryset, info.context.user)

        if is_field_selected(info, "edges.node.user"):
            queryset = queryset.select_related("user")

        return queryset

    def resolve_problems(self, info, **kwargs):  # noqa: WPS110
        """Get issue problems."""
        return get_issue_problems(self)

    def resolve_metrics(self, info, **kwargs):  # noqa: WPS110
        """Get issue metrics."""
        return metrics.get_issue_metrics(self)

    def resolve_time_spent(self, info, **kwargs):  # noqa: WPS110
        """Get user time spent."""
        if self.user:
            return metrics.get_user_time_spent(self, user=self.user)

        return 0
