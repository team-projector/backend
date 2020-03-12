# -*- coding: utf-8 -*-

import factory

from apps.users.models import Position


class PositionFactory(factory.django.DjangoModelFactory):
    title = factory.Faker("word")

    class Meta:
        model = Position
