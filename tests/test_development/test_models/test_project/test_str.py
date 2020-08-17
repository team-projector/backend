# -*- coding: utf-8 -*-

from tests.test_development.factories import ProjectFactory


def test_str(db):
    """
    Test str.

    :param db:
    """
    project = ProjectFactory.create(
        title="project_title_test", full_title="project_full_title_test",
    )

    assert str(project) == "project_full_title_test"


def test_null_full_title(db):
    """
    Test null full title.

    :param db:
    """
    project = ProjectFactory.create(
        title="project_title_test", full_title=None,
    )

    assert str(project) == "project_title_test"
