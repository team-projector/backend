from datetime import datetime

import pytest

from apps.development.graphql.mutations.issues.create import InputSerializer
from tests.test_development.factories import ProjectFactory


@pytest.fixture()
def project(db):
    """Create project."""
    return ProjectFactory.create()


@pytest.fixture()
def user_request(auth_rf):
    """Mock request."""
    return auth_rf.post("/")


def test_valid_data(user, project, user_request):
    """Test valid data."""
    user.gl_token = "token"
    user.save()

    serializer = InputSerializer(
        data=_source_data(user, project),
        context={"request": user_request},
    )

    assert serializer.is_valid()
    assert serializer.validated_data.get("author") == user


def test_no_valid_data(user, project, user_request):
    """Test no valid data."""
    serializer = InputSerializer(
        data=_source_data(user, project),
        context={"request": user_request},
    )

    assert not serializer.is_valid()


def _source_data(user, project):
    return {
        "title": "Create issue",
        "project": project.pk,
        "user": user.pk,
        "estimate": 100,
        "dueDate": str(datetime.now().date()),
    }
