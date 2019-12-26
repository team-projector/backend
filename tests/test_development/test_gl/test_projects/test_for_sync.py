# -*- coding: utf-8 -*-

from apps.development.models import Project
from tests.test_development.factories import ProjectFactory


def test_exists(db, gl_mocker):
    ProjectFactory.create()

    assert Project.objects.for_sync().count() == 1


def test_not_exists(db, gl_mocker):
    ProjectFactory.create(is_active=False)

    assert not Project.objects.for_sync().exists()
