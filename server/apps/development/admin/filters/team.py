from django.db import models
from jnt_admin_tools.autocomplete_filter import AutocompleteFilter

from apps.development.models import Team


class TeamFilter(AutocompleteFilter):
    """Autocomplete filter by team."""

    field_name = "team"
    title = "team"

    def get_remote_field(self, model):
        """Remote field."""
        project_field = model._meta.get_field("project")  # noqa: WPS437
        return project_field.related_model._meta.get_field(  # noqa: WPS437
            "team",
        ).remote_field

    def get_field_queryset(self, model) -> models.QuerySet:
        """Field queryset."""
        return Team.objects.all()

    def queryset(self, request, queryset) -> models.QuerySet:
        """Filter queryset by selected value."""
        from apps.development.graphql.fields import (  # noqa: WPS433
            issues_filters,
        )

        target_value = self.value()

        if not target_value:
            return queryset

        selected_team = Team.objects.filter(pk=target_value).first()
        if not selected_team:
            return queryset

        team_filter = issues_filters.TeamFilter()
        return team_filter.filter(queryset, selected_team)
