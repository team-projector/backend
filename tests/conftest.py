import httpretty
import pytest
from django.contrib.auth.models import AnonymousUser
from graphene.test import Client as GQLClient
from apps.users.models import User
from gql import schema
from tests.base import Client, create_user, USER_LOGIN, USER_PASSWORD
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


@pytest.fixture(scope='module')
def client():
    return Client()


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(USER_LOGIN, USER_PASSWORD)


@pytest.fixture
def admin_client(admin_user):
    return Client(admin_user)


@pytest.fixture
def gql_client_authenticated(rf, admin_user):
    request = rf.post('/')
    request.user = admin_user

    return GQLClient(schema, context_value=request)


@pytest.fixture
def gql_client_anonymous(rf):
    request = rf.post('/')
    request.user = AnonymousUser()

    return GQLClient(schema, context_value=request)
