from bitfield.rest.fields import BitField
from rest_framework import filters, serializers
from rest_framework.exceptions import ValidationError

from apps.core.utils.rest import parse_query_params
from apps.development.models import TeamMember
from apps.development.services.team_members import filter_by_roles


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
    roles = NoCastBitField(
        required=False,
        model=TeamMember
    )


class TeamMemberRoleFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        params = parse_query_params(request, TeamMemberRoleFilterSerializer)

        roles = params.get('roles')
        if roles:
            queryset = filter_by_roles(queryset, roles)

        return queryset
