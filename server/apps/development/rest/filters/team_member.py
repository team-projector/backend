from bitfield.rest.fields import BitField
from django.db.models import Exists, OuterRef
from rest_framework import filters, serializers
from rest_framework.exceptions import ValidationError

from apps.core.utils.rest import parse_query_params
from apps.development.models import TeamMember
from apps.development.services.team_members import filter_by_roles
from apps.users.models import User


# TODO refactor!
class NoCastBitField(BitField):
    def to_internal_value(self, data):
        model_field = self._get_model_field()
        flags = model_field.flags

        errors = []
        for choice in data:
            if choice not in flags:
                errors.append(ValidationError(f'Unknown choice: {choice}'))

        if errors:
            raise ValidationError(errors)

        return data


class TeamMemberRoleFilterSerializer(serializers.Serializer):
    roles = NoCastBitField(required=False, model=TeamMember)


class TeamMemberFilterSerializer(TeamMemberRoleFilterSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)


class TeamMemberFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        params = parse_query_params(request, TeamMemberFilterSerializer)

        user, roles = params.get('user'), params.get('roles')

        if all(param is not None for param in (user, roles)):
            team_members = filter_by_roles(
                TeamMember.objects.filter(
                    team=OuterRef('pk'),
                    user=user,
                ), roles)

            queryset = queryset.annotate(
                member_exists=Exists(team_members)
            ).filter(
                member_exists=True
            )

        return queryset


class TeamMemberRoleFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        params = parse_query_params(request, TeamMemberRoleFilterSerializer)

        roles = params.get('roles')
        if roles:
            queryset = filter_by_roles(queryset, roles)

        return queryset
