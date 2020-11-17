import factory

from apps.development.models import Project
from tests.test_development.factories.mixins.gl_field import GitlabFieldMixin


class ProjectFactory(GitlabFieldMixin):
    """Project factory."""

    class Meta:
        model = Project

    title = factory.Faker("sentence")
