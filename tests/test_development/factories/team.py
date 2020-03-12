# -*- coding: utf-8 -*-

import factory

from apps.development.models import Team


class TeamFactory(factory.django.DjangoModelFactory):
    title = factory.Faker("text", max_nb_chars=200)

    class Meta:
        model = Team

    @factory.post_generation
    def members(self, create, extracted, **kwargs):
        if create and extracted:
            self.members.set(extracted)
