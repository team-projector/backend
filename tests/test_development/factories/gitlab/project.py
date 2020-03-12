# -*- coding: utf-8 -*-

import factory


class GlProjectFactory(factory.DictFactory):
    id = factory.Faker("random_int")
    description = factory.Faker("word")
    name = factory.Sequence(lambda seq: "Project {0}".format(seq))
    web_url = factory.Faker("url")
    avatar_url = factory.Faker("url")
    name_with_namespace = factory.Faker("word")
    archived = False
