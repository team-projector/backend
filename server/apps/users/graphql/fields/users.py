import django_filters
import graphene
from jnt_django_graphene_toolbox.fields import BaseModelConnectionField

from apps.core.graphql.queries.filters import OrderingFilter
from apps.users.models import User


class UserFilterSet(django_filters.FilterSet):
    """Set of filters for User."""

    class Meta:
        model = User
        fields = ("is_active",)

    order_by = OrderingFilter(fields=("login", "name"))


class UserSort(graphene.Enum):
    """Allowed sort fields."""

    LOGIN_ASC = "login"  # noqa: WPS115
    LOGIN_DESC = "-login"  # noqa: WPS115
    NAME_ASC = "name"  # noqa: WPS115
    NAME_DESC = "-name"  # noqa: WPS115


class UsersConnectionField(BaseModelConnectionField):
    """Handler for users collections."""

    filterset_class = UserFilterSet
    auth_required = True

    def __init__(self):
        """Initialize."""
        super().__init__(
            "apps.users.graphql.types.UserType",
            is_active=graphene.Boolean(),
            order_by=graphene.Argument(graphene.List(UserSort)),
        )
