# -*- coding: utf-8 -*-

import django_filters
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from jnt_django_graphene_toolbox.filters import OrderingFilter

from apps.development.models import Team, TeamMember

User = get_user_model()


def filter_allowed_for_user(
    queryset: QuerySet,
    user: User,  # type: ignore
):
    """Filter work breaks for user."""
    users = TeamMember.objects.filter(
        user=user,
        roles=TeamMember.roles.LEADER,
    ).values_list("team__members", flat=True)

    return queryset.filter(id__in=(*users, user.id))  # type: ignore


class UserFilter(django_filters.ModelChoiceFilter):
    """Filter workbreaks by user."""

    def __init__(self) -> None:
        """Initialize self."""
        super().__init__(queryset=User.objects.all())

    def filter(  # noqa: WPS125, A003
        self,
        queryset,
        value,  # noqa: WPS110
    ) -> QuerySet:
        """Do filtering."""
        if not value:
            return queryset

        return queryset.filter(id=value.id)


class TeamFilter(django_filters.ModelChoiceFilter):
    """Filter workbreaks by team."""

    def __init__(self) -> None:
        """Initialize self."""
        super().__init__(queryset=Team.objects.all())

    def filter(  # noqa: WPS125, A003
        self,
        queryset,
        value,  # noqa: WPS110
    ) -> QuerySet:
        """Do filtering."""
        if not value:
            return queryset

        users = TeamMember.objects.get_no_watchers(value)
        return queryset.filter(id__in=users)


class UserWorkBreaksFilterSet(django_filters.FilterSet):
    """Set of filters for UserWorkBreak."""

    class Meta:
        model = User
        fields = ("name", "email")

    user = UserFilter()
    team = TeamFilter()

    order_by = OrderingFilter(fields=("name", "email"))

    def filter_queryset(self, queryset):
        """Filtering queryset."""
        queryset = super().filter_queryset(queryset)

        return filter_allowed_for_user(queryset, self.request.user)
