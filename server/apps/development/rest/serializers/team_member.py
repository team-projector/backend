from bitfield.rest.fields import BitField
from rest_framework import serializers

from apps.users.rest.serializers import UserCardSerializer
from ...models import TeamMember


class TeamMemberCardSerializer(serializers.ModelSerializer):
    roles = BitField()
    user = UserCardSerializer()

    class Meta:
        model = TeamMember
        fields = ('id', 'user', 'roles')
