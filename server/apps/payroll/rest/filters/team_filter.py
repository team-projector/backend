from rest_framework import filters


class TeamFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        team_param = request.GET.get('team')

        if team_param and team_param.isdigit():
            queryset = queryset.filter(user__teams=team_param)

        return queryset
