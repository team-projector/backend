from rest_framework import filters


class TeamFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        team_param = request.GET.get('team')

        if not team_param:
            return queryset

        if team_param.isdigit():
            queryset = queryset.filter(user__team_members__team_id=team_param)

        return queryset
