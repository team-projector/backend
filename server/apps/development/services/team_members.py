# -*- coding: utf-8 -*-

from functools import reduce
from operator import or_
from typing import Iterable, Union

from bitfield import Bit
from django.db.models import Q, QuerySet


def filter_by_roles(queryset: QuerySet,
                    roles: Iterable[Union[str, Bit]]) -> QuerySet:
    from apps.development.models import TeamMember

    roles = [
        role
        if isinstance(role, Bit) else
        Bit(TeamMember.roles.keys().index(role))
        for role in roles
    ]

    return queryset.filter(
        reduce(
            or_,
            [Q(roles=role) for role in roles],
        ),
    )
