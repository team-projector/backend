import factory

from apps.development.models import Milestone
from tests.test_development.factories.milestone import MilestoneFactory
from tests.test_development.factories.project_group import ProjectGroupFactory


class ProjectGroupMilestoneFactory(MilestoneFactory):
    owner = factory.SubFactory(ProjectGroupFactory)

    class Meta:
        model = Milestone
