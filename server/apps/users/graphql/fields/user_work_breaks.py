from django.db.models import QuerySet
from graphql import ResolveInfo

from apps.core.graphql.fields import BaseModelConnectionField


class UserWorkBreaksConnectionField(BaseModelConnectionField):
    """Handler for user workbreaks collections."""

    def __init__(self):
        """Initialize."""
        super().__init__("payroll.WorkBreakType")

    @classmethod
    def resolve_queryset(
        cls,
        connection,
        queryset: QuerySet,
        info: ResolveInfo,  # noqa: WPS110
        args,
    ):
        """Filter queryset."""
        return queryset.order_by("from_date")
