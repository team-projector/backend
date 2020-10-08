import factory

from apps.development.models import Milestone
from tests.test_development.factories.milestone import MilestoneFactory
from tests.test_development.factories.project import ProjectFactory


class ProjectMilestoneFactory(MilestoneFactory):
    """Project milestone factory."""

    class Meta:
        model = Milestone

    owner = factory.SubFactory(ProjectFactory)
