from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.core.rest.serializers import LinkSerializer
from apps.development.models import TeamMember
from apps.payroll.models import WorkBreak
from apps.users.rest.serializers import UserCardSerializer

User = get_user_model()


class WorkBreakSerializer(serializers.ModelSerializer):
    approved_by = UserCardSerializer()
    user = LinkSerializer()
    approved_at = serializers.DateTimeField()
    from_date = serializers.DateTimeField()
    to_date = serializers.DateTimeField()

    class Meta:
        model = WorkBreak
        fields = (
            'approve_state', 'approved_by', 'approved_at', 'decline_reason',
            'comment', 'from_date', 'reason', 'to_date', 'id', 'user'
        )


class WorkBreakCardSerializer(WorkBreakSerializer):
    approved_by = LinkSerializer()


class WorkBreakUpdateSerializer(serializers.ModelSerializer):
    def validate_user(self, user):
        if user == self.context['request'].user:
            return user

        teams = TeamMember.objects.filter(
            user=self.context['request'].user,
            roles=TeamMember.roles.leader
        ).values_list(
            'team',
            flat=True
        )

        if User.objects.filter(team_members__team__in=teams,
                               team_members__roles=TeamMember.roles.developer,
                               id=user.id).exists():
            return user

        raise serializers.ValidationError(
            _('MSG_USER_CAN_NOT_MANAGE_CURRENT_WORKBREAK'))

    class Meta:
        model = WorkBreak
        fields = ('comment', 'from_date', 'reason', 'to_date', 'user')
