# -*- coding: utf-8 -*-

import factory

from apps.development.models import ProjectGroup
from tests.test_development.factories.mixins.gl_field import GitlabFieldMixin


class ProjectGroupFactory(GitlabFieldMixin):
    """Project group factory."""

    class Meta:
        model = ProjectGroup

    title = factory.Faker("text", max_nb_chars=200)
