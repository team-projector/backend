# -*- coding: utf-8 -*-

import factory

from apps.development.models import Team


class TeamFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Team

    title = factory.Faker("text", max_nb_chars=200)

    @factory.post_generation
    def members(self, create, extracted, **kwargs):
        if create and extracted:
            self.members.set(extracted)
