from django.test import override_settings

from apps.development.services.gitlab.groups import load_single_group, load_groups
from apps.development.models import ProjectGroup

from tests.test_development.factories import ProjectGroupFactory
from tests.test_development.factories_gitlab import AttrDict, GlUserFactory, GlGroupFactory
from tests.test_development.mocks import activate, registry_get_gl_url


def test_load_single_group(db):
    gl_group = AttrDict(GlGroupFactory())

    group = load_single_group(gl_group, None)

    _check_group(group, gl_group)


def test_load_single_group_with_parent(db):
    parent = ProjectGroupFactory.create()
    gl_group = AttrDict(GlGroupFactory(parent_id=parent.id))

    group = load_single_group(gl_group, parent)

    _check_group(group, gl_group, parent)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
@activate
def test_load_groups(db):
    gl_group_1 = AttrDict(GlGroupFactory())
    gl_group_2 = AttrDict(GlGroupFactory(parent_id=gl_group_1.id))

    registry_get_gl_url('https://gitlab.com/api/v4/user', GlUserFactory())
    registry_get_gl_url('https://gitlab.com/api/v4/groups', [gl_group_1, gl_group_2])

    load_groups()

    group_1 = ProjectGroup.objects.get(gl_id=gl_group_1.id)
    _check_group(group_1, gl_group_1)

    group_2 = ProjectGroup.objects.get(gl_id=gl_group_2.id)
    _check_group(group_2, gl_group_2, group_1)


def _check_group(group, gl_group, parent=None):
    assert group.gl_id == gl_group.id
    assert group.gl_url == gl_group.web_url
    assert group.title == gl_group.name
    assert group.full_title == gl_group.full_name

    if not parent:
        assert group.parent is None
    else:
        assert group.parent == parent
