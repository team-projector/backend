import django_filters
import graphene

from apps.core.graphql.fields import BaseModelConnectionField
from apps.core.graphql.queries.filters import OrderingFilter
from apps.users.models import User


class UserFilterSet(django_filters.FilterSet):
    """Set of filters for User."""

    class Meta:
        model = User
        fields = ("is_active",)

    order_by = OrderingFilter(fields=("login", "name"))


class AllUsersConnectionField(BaseModelConnectionField):
    """Handler for users collections."""

    filterset_class = UserFilterSet

    def __init__(self):
        """Initialize."""
        super().__init__(
            "users.UserType",
            is_active=graphene.Boolean(),
            order_by=graphene.String(),  # "login", "name"
        )
