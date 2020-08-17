# -*- coding: utf-8 -*-

from tests.test_development.factories import ProjectGroupFactory


def test_str(db):
    """
    Test str.

    :param db:
    """
    group = ProjectGroupFactory.create(title="group_title_test")

    assert str(group) == "group_title_test"
