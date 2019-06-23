from rest_framework import serializers

from apps.development.models import Team
from .team_member import TeamMemberCardSerializer


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('id', 'title')


class TeamCardSerializer(serializers.ModelSerializer):
    members_count = serializers.SerializerMethodField()
    members = TeamMemberCardSerializer(many=True)

    @staticmethod
    def get_members_count(instance):
        return instance.members.count()

    class Meta:
        model = Team
        fields = ('id', 'title', 'members_count', 'members')
