# -*- coding: utf-8 -*-

import factory

from apps.users.models import User


class UserFactory(factory.django.DjangoModelFactory):
    login = factory.Sequence(lambda seq: "User {0}".format(seq))
    name = factory.Sequence(lambda seq: "User name {0}".format(seq))
    hour_rate = factory.Faker("random_int", min=100, max=999)
    is_staff = False
    is_active = True

    class Meta:
        model = User
