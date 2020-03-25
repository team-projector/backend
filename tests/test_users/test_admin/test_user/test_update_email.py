# -*- coding: utf-8 -*-

from http import HTTPStatus

from tests.test_users.factories.user import UserFactory


def test_change_email(user_admin, admin_client):
    """Test normal email update."""
    user = UserFactory.create(email="old_@mail.com")

    data = {
        "email": "new_@mail.com",
        "hour_rate": user.hour_rate,
        "customer_hour_rate": user.customer_hour_rate,
        "tax_rate": user.tax_rate,
        "daily_work_hours": user.daily_work_hours,
        "annual_paid_work_breaks_days": user.annual_paid_work_breaks_days,
    }

    response = user_admin.changeform_view(
        admin_client.post("/admin/users/user/", data), object_id=str(user.id),
    )

    assert response.status_code == HTTPStatus.FOUND

    user.refresh_from_db()
    assert user.email == "new_@mail.com"


def test_not_changed_email(user_admin, admin_client):
    """Test same email update."""
    user = UserFactory.create(email="test@mail.com")

    data = {
        "email": "test@mail.com",
        "hour_rate": user.hour_rate,
        "customer_hour_rate": user.customer_hour_rate,
        "tax_rate": user.tax_rate,
        "daily_work_hours": user.daily_work_hours,
    }

    user_admin.changeform_view(
        admin_client.post("/admin/users/user/", data), object_id=str(user.id),
    )

    user.refresh_from_db()
    assert user.email == "test@mail.com"


def test_dublicate_email(user_admin, admin_client):
    """Test dublicate email validation."""
    user = UserFactory.create(email="user@mail.com")
    another_user = UserFactory.create(email="another_user@mail.com")

    data = {
        "email": user.email,
        "hour_rate": another_user.hour_rate,
        "customer_hour_rate": another_user.customer_hour_rate,
        "tax_rate": another_user.tax_rate,
        "daily_work_hours": another_user.daily_work_hours,
    }

    response = user_admin.changeform_view(
        admin_client.post("/admin/users/user/", data),
        object_id=str(another_user.id),
    )

    assert response.context_data["errors"]

    another_user.refresh_from_db()
    assert another_user.email == "another_user@mail.com"
