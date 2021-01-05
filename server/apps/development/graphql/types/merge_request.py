import graphene
from django.db import models

from apps.core import graphql
from apps.core.graphql.nodes import ModelRelayNode
from apps.core.graphql.types import BaseModelObjectType
from apps.development import models as development_models
from apps.development.graphql import fields, interfaces
from apps.development.graphql.types import MergeRequestMetricsType
from apps.development.services.merge_request.allowed import (
    filter_allowed_for_user,
)
from apps.development.services.merge_request.metrics import (
    get_merge_request_metrics,
)
from apps.development.services.merge_request.problems import (
    get_merge_request_problems,
)
from apps.users.graphql.fields import UsersConnectionField


class MergeRequestType(BaseModelObjectType):
    """Merge request type."""

    class Meta:
        model = development_models.MergeRequest
        interfaces = (ModelRelayNode, interfaces.WorkItem)
        auth_required = True

    gl_url = graphene.String()
    gl_last_sync = graphene.DateTime()
    title = graphene.String()
    time_estimate = graphene.Int()
    total_time_spent = graphene.Int()
    state = graphene.Field(
        graphene.Enum.from_enum(
            development_models.merge_request.MergeRequestState,
        ),
    )
    created_at = graphene.DateTime()
    updated_at = graphene.DateTime()
    closed_at = graphene.DateTime()
    labels = fields.LabelsConnectionField()
    project = graphene.Field("apps.development.graphql.types.ProjectType")
    user = graphene.Field("apps.users.graphql.types.UserType")
    author = graphene.Field("apps.users.graphql.types.UserType")
    milestone = graphene.Field("apps.development.graphql.types.MilestoneType")
    participants = UsersConnectionField()
    metrics = graphene.Field(MergeRequestMetricsType)
    problems = graphene.List(graphene.String)

    @classmethod
    def get_queryset(cls, queryset, info) -> models.QuerySet:  # noqa: WPS110
        """Get queryset."""
        queryset = filter_allowed_for_user(queryset, info.context.user)

        if graphql.is_field_selected(info, "edges.node.user"):
            queryset = queryset.select_related("user")

        return queryset

    def resolve_metrics(self, info, **kwargs):  # noqa: WPS110
        """Get merge request metrics."""
        return get_merge_request_metrics(self)

    def resolve_problems(self, info, **kwargs):  # noqa: WPS110
        """Get merge request problems."""
        return get_merge_request_problems(self)
