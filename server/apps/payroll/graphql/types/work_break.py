from django.db.models import QuerySet
from jnt_django_graphene_toolbox.connections import DataSourceConnection
from jnt_django_graphene_toolbox.relay_nodes import DatasourceRelayNode
from jnt_django_graphene_toolbox.types import BaseDjangoObjectType

from apps.payroll.models import WorkBreak
from apps.payroll.services.work_break.allowed import filter_allowed_for_user


class WorkBreakType(BaseDjangoObjectType):
    """Work break type."""

    class Meta:
        model = WorkBreak
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        name = "WorkBreak"

    @classmethod
    def get_queryset(cls, queryset, info) -> QuerySet:  # noqa: WPS110
        """Get work breaks."""
        return filter_allowed_for_user(queryset, info.context.user)
