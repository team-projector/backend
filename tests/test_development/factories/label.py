# -*- coding: utf-8 -*-

import factory

from apps.development.models import Label


class LabelFactory(factory.django.DjangoModelFactory):
    title = factory.Faker("text", max_nb_chars=200)
    color = factory.Faker("text", max_nb_chars=10)

    class Meta:
        model = Label
