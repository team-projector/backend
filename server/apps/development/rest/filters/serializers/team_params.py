from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.development.models import Team, TeamMember
from apps.development.services.team_members import filter_by_roles


class TeamParamsSerializer(serializers.Serializer):
    team = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(),
        required=False
    )

    def validate_team(self, value):
        self._check_allowed_filtering(value)
        return value

    def _check_allowed_filtering(self, value):
        queryset = TeamMember.objects.filter(
            team=value,
            user=self.context['request'].user
        )

        can_filtering = filter_by_roles(
            queryset,
            [
                TeamMember.roles.leader,
                TeamMember.roles.watcher
            ]
        ).exists()

        if not can_filtering:
            raise ValidationError('Can\'t filter by team')
