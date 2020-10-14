from jnt_django_toolbox.helpers.objects import dict2obj

from apps.development.models import ProjectGroup
from apps.development.services.project_group.gl.manager import (
    ProjectGroupGlManager,
)
from tests.test_development.factories import ProjectGroupFactory
from tests.test_development.factories.gitlab import GlGroupFactory
from tests.test_development.test_gl.helpers import gl_checkers, gl_mock


def test_load_all(db, gl_mocker):
    """
    Test load all.

    :param db:
    :param gl_mocker:
    """
    parent_gl_group = GlGroupFactory.create()
    child_gl_group = GlGroupFactory(parent_id=parent_gl_group["id"])

    gl_mock.register_groups(gl_mocker, [parent_gl_group, child_gl_group])

    ProjectGroupGlManager().sync_groups()

    parent_group = ProjectGroup.objects.get(gl_id=parent_gl_group["id"])
    gl_checkers.check_group(parent_group, parent_gl_group)
    child_group = ProjectGroup.objects.get(gl_id=child_gl_group["id"])
    gl_checkers.check_group(child_group, child_gl_group, parent_group)


def test_load_filtered(db, gl_mocker):
    """
    Test load filtered.

    :param db:
    :param gl_mocker:
    """
    parent_gl_group = GlGroupFactory.create()
    another_parent_gl_group = GlGroupFactory.create()

    child_gl_group = GlGroupFactory(parent_id=parent_gl_group["id"])
    another_child_gl_group = GlGroupFactory(
        parent_id=another_parent_gl_group["id"],
    )

    gl_mock.register_groups(
        gl_mocker,
        [
            parent_gl_group,
            child_gl_group,
            another_parent_gl_group,
            another_child_gl_group,
        ],
    )

    ProjectGroupGlManager().sync_groups(filter_ids=[parent_gl_group["id"]])

    parent_group = ProjectGroup.objects.get(gl_id=parent_gl_group["id"])
    gl_checkers.check_group(parent_group, parent_gl_group)
    child_group = ProjectGroup.objects.get(gl_id=child_gl_group["id"])
    gl_checkers.check_group(child_group, child_gl_group, parent_group)

    assert not ProjectGroup.objects.filter(
        gl_id__in=[
            another_parent_gl_group["id"],
            another_child_gl_group["id"],
        ],
    ).exists()


def test_single_group(db):
    """
    Test single group.

    :param db:
    """
    gl_group = GlGroupFactory.create()

    group = ProjectGroupGlManager().update_group(dict2obj(gl_group), None)

    gl_checkers.check_group(group, gl_group)


def test_single_group_with_parent(db):
    """
    Test single group with parent.

    :param db:
    """
    gl_parent = GlGroupFactory.create()
    parent = ProjectGroupFactory.create(gl_id=gl_parent["id"])

    gl_group = GlGroupFactory.create(parent_id=parent.gl_id)

    group = ProjectGroupGlManager().update_group(dict2obj(gl_group), parent)

    gl_checkers.check_group(group, gl_group, parent)
