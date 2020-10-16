import django_filters
from django.contrib.auth import get_user_model
from jnt_django_graphene_toolbox.filters import OrderingFilter

User = get_user_model()


class UserFilterSet(django_filters.FilterSet):
    """Set of filters for User."""

    class Meta:
        model = User
        fields = ("is_active",)

    order_by = OrderingFilter(fields=("login", "name"))
