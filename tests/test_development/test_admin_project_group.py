from rest_framework import status

from apps.development.models import ProjectGroup
from tests.base import model_admin
from tests.test_development.checkers_gitlab import check_group
from tests.test_development.factories import ProjectGroupFactory
from tests.test_development.factories_gitlab import (
    AttrDict, GlGroupFactory, GlUserFactory,
)


def test_sync_handler(db, gl_mocker):
    ma_group = model_admin(ProjectGroup)

    gl_mocker.registry_get('/user', GlUserFactory())

    gl_group = AttrDict(GlGroupFactory())
    group = ProjectGroupFactory.create(gl_id=gl_group.id)
    gl_mocker.registry_get(f'/groups/{gl_group.id}', gl_group)

    ma_group.sync_handler(group)

    group = ProjectGroup.objects.first()

    check_group(group, gl_group)


def test_force_sync(admin_client):
    ma_group = model_admin(ProjectGroup)

    group = ProjectGroupFactory.create(title='created')

    data = {
        '_force_sync': ['Force sync'],
        'gl_id': group.gl_id,
        'gl_url': group.gl_url,
        'title': 'updated',
        'development-projectmember-content_type-object_id-TOTAL_FORMS': ['0'],
        'development-projectmember-content_type-object_id-INITIAL_FORMS': ['0'],
        'development-projectmember-content_type-object_id-MIN_NUM_FORMS': ['0'],
        'development-projectmember-content_type-object_id-MAX_NUM_FORMS': ['1000'],
        'development-projectmember-content_type-object_id-__prefix__-id': [''],
        'development-projectmember-content_type-object_id-__prefix__-role': [''],
    }

    response = ma_group.change_view(
        request=admin_client.post('/', data),
        object_id=str(group.id)
    )

    assert response.status_code == status.HTTP_302_FOUND

    group = ProjectGroup.objects.first()

    assert group.title == 'updated'


def test_sync_obj(admin_client):
    ma_group = model_admin(ProjectGroup)

    group = ProjectGroupFactory.create(title='created')

    data = {
        'gl_id': group.gl_id,
        'gl_url': group.gl_url,
        'title': 'updated',
        'development-projectmember-content_type-object_id-TOTAL_FORMS': ['0'],
        'development-projectmember-content_type-object_id-INITIAL_FORMS': ['0'],
        'development-projectmember-content_type-object_id-MIN_NUM_FORMS': ['0'],
        'development-projectmember-content_type-object_id-MAX_NUM_FORMS': ['1000'],
        'development-projectmember-content_type-object_id-__prefix__-id': [''],
        'development-projectmember-content_type-object_id-__prefix__-role': [''],
    }

    response = ma_group.change_view(
        request=admin_client.post('/', data),
        object_id=str(group.id)
    )

    assert response.status_code == status.HTTP_302_FOUND
