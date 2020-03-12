# -*- coding: utf-8 -*-

import factory

from apps.development.models import TeamMember


class TeamMemberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TeamMember
