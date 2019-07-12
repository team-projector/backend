import httpretty
import pytest

from apps.users.models import User
from tests.base import (
    TestClient, TestAPIClient, create_user, USER_LOGIN, USER_PASSWORD
)
from tests.mocks import GitlabMock


def pytest_addoption(parser):
    parser.addoption(
        '--runslow', action='store_true', default=False, help='run slow tests'
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption('--runslow'):
        skip = pytest.mark.skip(reason='--runslow runs only marked as slow tests')
        for item in items:
            if 'slow' not in item.keywords:
                item.add_marker(skip)
    else:
        skip = pytest.mark.skip(reason='need --runslow option to run')
        for item in items:
            if 'slow' in item.keywords:
                item.add_marker(skip)


@pytest.fixture(autouse=True, scope='function')
def media_root(settings, tmpdir_factory):
    settings.MEDIA_ROOT = tmpdir_factory.mktemp('media', numbered=True)


@pytest.fixture(autouse=True, scope='function')
def password_hashers(settings):
    settings.PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ]


@pytest.fixture()
def gl_mocker():
    httpretty.enable(allow_net_connect=False)

    yield GitlabMock()

    httpretty.disable()


@pytest.fixture()
def user(db):
    return create_user()


@pytest.fixture()
def admin_user(db):
    return User.objects.create_superuser(USER_LOGIN, USER_PASSWORD)


@pytest.fixture()
def api_client():
    return TestAPIClient()


@pytest.fixture()
def admin_client(admin_user):
    return TestClient(admin_user)
