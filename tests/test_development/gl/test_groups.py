from django.test import override_settings

from apps.development.services.gitlab.groups import (
    load_single_group, load_groups
)
from apps.development.models import ProjectGroup


from tests.test_development.checkers_gitlab import check_group
from tests.test_development.factories import ProjectGroupFactory
from tests.test_development.factories_gitlab import (
    AttrDict, GlUserFactory, GlGroupFactory
)


def test_load_single_group(db):
    gl_group = AttrDict(GlGroupFactory())

    group = load_single_group(gl_group, None)

    check_group(group, gl_group)


def test_load_single_group_with_parent(db):
    gl_parent = AttrDict(GlGroupFactory())
    parent = ProjectGroupFactory.create(gl_id=gl_parent.id)

    gl_group = AttrDict(GlGroupFactory(parent_id=parent.gl_id))

    group = load_single_group(gl_group, parent)

    check_group(group, gl_group, parent)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_groups(db, gl_mocker):
    gl_group_1 = AttrDict(GlGroupFactory())
    gl_group_2 = AttrDict(GlGroupFactory(parent_id=gl_group_1.id))

    gl_mocker.registry_get('/user', GlUserFactory())
    gl_mocker.registry_get('/groups', [gl_group_1, gl_group_2])

    load_groups()

    group_1 = ProjectGroup.objects.get(gl_id=gl_group_1.id)
    check_group(group_1, gl_group_1)

    group_2 = ProjectGroup.objects.get(gl_id=gl_group_2.id)
    check_group(group_2, gl_group_2, group_1)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_groups_parent_first(db, gl_mocker):
    gl_group_1 = AttrDict(GlGroupFactory())
    gl_group_2 = AttrDict(GlGroupFactory(parent_id=gl_group_1.id))

    gl_mocker.registry_get('/user', GlUserFactory())
    gl_mocker.registry_get('/groups', [gl_group_2, gl_group_1])

    load_groups()

    group_1 = ProjectGroup.objects.get(gl_id=gl_group_1.id)
    check_group(group_1, gl_group_1)

    group_2 = ProjectGroup.objects.get(gl_id=gl_group_2.id)
    check_group(group_2, gl_group_2, group_1)