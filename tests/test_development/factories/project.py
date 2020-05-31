# -*- coding: utf-8 -*-

import factory

from apps.development.models import Project
from tests.test_development.factories.mixins.gl_field import GitlabFieldMixin


class ProjectFactory(GitlabFieldMixin):
    class Meta:
        model = Project

    title = factory.Faker("text", max_nb_chars=200)
