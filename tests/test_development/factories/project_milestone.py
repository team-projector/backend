# -*- coding: utf-8 -*-

import factory

from apps.development.models import Milestone
from tests.test_development.factories.milestone import MilestoneFactory
from tests.test_development.factories.project import ProjectFactory


class ProjectMilestoneFactory(MilestoneFactory):
    owner = factory.SubFactory(ProjectFactory)

    class Meta:
        model = Milestone
