import pytest

from apps.core import injector
from apps.users.logic.services import IUserProblemsService
from tests.test_users.factories import UserFactory


@pytest.fixture()
def user(db):
    """Provides test user."""
    return UserFactory.create(daily_work_hours=8)


@pytest.fixture()
def user_problems_service():
    """Provides user problems service."""
    return injector.get(IUserProblemsService)
