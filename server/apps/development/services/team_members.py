# -*- coding: utf-8 -*-

from functools import reduce
from operator import or_
from typing import Iterable, Union

from django.db import models
from jnt_django_toolbox.models.fields.bit.types import Bit

from apps.development.models import TeamMember


def filter_by_roles(
    queryset: models.QuerySet,
    roles: Iterable[Union[str, Bit]],
) -> models.QuerySet:
    """Get team members by role."""
    roles = [
        role
        if isinstance(role, Bit)
        else Bit(TeamMember.roles.keys().index(role))
        for role in roles
    ]

    return queryset.filter(
        reduce(or_, [models.Q(roles=role) for role in roles]),
    )
