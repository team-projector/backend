# -*- coding: utf-8 -*-

from tests.test_development.factories import (
    ProjectFactory,
    ProjectMilestoneFactory,
)


def test_str(db):
    project = ProjectFactory.create(title="project_title_test")
    milestone = ProjectMilestoneFactory.create(
        title="milestone_title_test", owner=project,
    )

    assert str(milestone) == "project_title_test / milestone_title_test"
