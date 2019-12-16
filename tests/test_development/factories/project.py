import factory

from apps.development.models import Project
from tests.test_development.factories.mixins.gl_field import GitlabFieldMixin


class ProjectFactory(GitlabFieldMixin):
    title = factory.Faker('text', max_nb_chars=200)

    class Meta:
        model = Project
