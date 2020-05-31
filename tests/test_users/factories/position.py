# -*- coding: utf-8 -*-

import factory

from apps.users.models import Position


class PositionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Position

    title = factory.Faker("word")
