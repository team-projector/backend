from datetime import datetime, timedelta

import pytest

from apps.development.use_cases.issues.create import InputDtoSerializer
from tests.test_development.factories import ProjectFactory


@pytest.fixture()
def project(db):
    """Create project."""
    return ProjectFactory.create()


@pytest.fixture()
def context(auth_rf):
    """Mock context."""
    return {"request": auth_rf.post("/")}


def test_valid_data(user, project, context):
    """Test valid data."""
    user.gl_token = "token"
    user.save()

    serializer = InputDtoSerializer(
        data=_source_data(user, project),
        context=context,
    )

    assert serializer.is_valid()


def test_estimate_as_none(user, project, context):
    """Test valid data."""
    user.gl_token = "token"
    user.save()

    estimate_field = "estimate"

    source_data = _source_data(user, project)
    source_data[estimate_field] = None
    serializer = InputDtoSerializer(
        data=source_data,
        context=context,
    )

    assert serializer.is_valid()
    assert serializer.validated_data.get(estimate_field) == 0


@pytest.mark.parametrize(
    ("field", "field_value"),
    [
        ("estimate", -1),
        ("due_date", str((datetime.now() - timedelta(days=2)).date())),
    ],
)
def test_no_valid_fields(user, project, context, field, field_value):
    """Test no valid fields."""
    user.gl_token = "token"
    user.save()

    source_data = _source_data(user, project)
    source_data[field] = field_value
    serializer = InputDtoSerializer(
        data=source_data,
        context=context,
    )

    assert not serializer.is_valid()
    assert len(serializer.errors) == 1
    assert field in serializer.errors


def _source_data(user, project):
    return {
        "title": "Create issue",
        "project": project.pk,
        "user": user.pk,
        "estimate": 100,
        "labels": None,
        "due_date": str(datetime.now().date()),
        "milestone": None,
    }
