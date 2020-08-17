# -*- coding: utf-8 -*-

from tests.test_development.factories import LabelFactory


def test_str(db):
    """
    Test str.

    :param db:
    """
    label = LabelFactory.create(title="label_title_test")

    assert str(label) == "label_title_test"
