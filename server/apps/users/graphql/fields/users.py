import django_filters
import graphene
from jnt_django_graphene_toolbox.fields import BaseModelConnectionField
from jnt_django_graphene_toolbox.filters import SortHandler

from apps.users.models import User


class UserSort(graphene.Enum):
    """Allowed sort fields."""

    LOGIN_ASC = "login"  # noqa: WPS115
    LOGIN_DESC = "-login"  # noqa: WPS115
    NAME_ASC = "name"  # noqa: WPS115
    NAME_DESC = "-name"  # noqa: WPS115


class UserFilterSet(django_filters.FilterSet):
    """Set of filters for User."""

    class Meta:
        model = User
        fields = "__all__"

    is_active = django_filters.BooleanFilter()


class UsersConnectionField(BaseModelConnectionField):
    """Handler for users collections."""

    auth_required = True
    sort_handler = SortHandler(UserSort)
    filterset_class = UserFilterSet

    def __init__(self):
        """Initialize."""
        super().__init__(
            "apps.users.graphql.types.UserType",
            is_active=graphene.Boolean(),
        )
