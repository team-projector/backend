from functools import reduce
from operator import or_
from typing import List, Union

from bitfield import Bit
from django.db.models import Q, QuerySet

from apps.development.models import TeamMember


def filter_by_roles(queryset: QuerySet,
                    roles: List[Union[str, Bit]]) -> QuerySet:
    roles = [
        role if isinstance(role, Bit) else Bit(TeamMember.roles.keys().index(role))
        for role in roles
    ]

    return queryset.filter(
        reduce(or_, [Q(roles=role) for role in roles])
    )
