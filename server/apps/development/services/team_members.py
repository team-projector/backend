# -*- coding: utf-8 -*-

from functools import reduce
from operator import or_
from typing import Iterable, Union

from bitfield import Bit
from django.db import models
from django.db.models import QuerySet

from apps.development.models import TeamMember


def filter_by_roles(
    queryset: QuerySet,
    roles: Iterable[Union[str, Bit]],
) -> QuerySet:
    """Get team members by role."""
    roles = [
        role
        if isinstance(role, Bit) else
        Bit(TeamMember.roles.keys().index(role))
        for role in roles
    ]

    return queryset.filter(
        reduce(
            or_,
            [models.Q(roles=role) for role in roles],
        ),
    )
