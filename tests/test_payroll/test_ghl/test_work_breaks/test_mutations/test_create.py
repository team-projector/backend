from datetime import date, timedelta

import pytest
from django.utils import timezone

from apps.core.gitlab import GITLAB_DATE_FORMAT
from apps.payroll.graphql.mutations.work_breaks.create import InputSerializer
from apps.payroll.models.work_break import WorkBreak, WorkBreakReason

CURRENT_YEAR = timezone.now().year


def test_query(user, ghl_client, ghl_raw):
    """Test create raw query."""
    ghl_client.set_user(user)

    create_variables = {
        "user": user.id,
        "fromDate": _date_strftime(timezone.now()),
        "toDate": _date_strftime(timezone.now() + timedelta(seconds=10)),
        "reason": WorkBreakReason.DAYOFF,
        "comment": "test comment",
        "paidDays": 3,
    }

    response = ghl_client.execute(
        ghl_raw("create_work_break"),
        variable_values=create_variables,
    )

    dto = response["data"]["createWorkBreak"]["workBreak"]

    assert WorkBreak.objects.count() == 1
    assert dto["comment"] == create_variables["comment"]
    assert dto["user"]["id"] == str(user.id)
    assert dto["paidDays"] == create_variables["paidDays"]


@pytest.mark.parametrize(
    ("from_date", "to_date", "paid_days"),
    [
        (
            date(CURRENT_YEAR, 2, 3),
            date(CURRENT_YEAR, 2, 10),
            7,
        ),
        (
            date(CURRENT_YEAR - 1, 12, 28),
            date(CURRENT_YEAR, 1, 3),
            2,
        ),
        (
            date(CURRENT_YEAR - 1, 12, 28),
            date(CURRENT_YEAR, 1, 1),
            0,
        ),
        (
            date(CURRENT_YEAR, 12, 27),
            date(CURRENT_YEAR + 1, 1, 3),
            5,
        ),
        (
            date(CURRENT_YEAR - 1, 1, 1),
            date(CURRENT_YEAR - 1, 2, 2),
            0,
        ),
        (
            date(CURRENT_YEAR + 1, 1, 1),
            date(CURRENT_YEAR + 1, 2, 2),
            0,
        ),
    ],
)
def test_fill_paid_days(user, from_date, to_date, paid_days):
    """Test fill paid days."""
    input_data = {
        "from_date": _date_strftime(from_date),
        "to_date": _date_strftime(to_date),
        "comment": "test",
        "reason": str(WorkBreakReason.VACATION),
        "user": user.pk,
    }

    serializer = InputSerializer(data=input_data)

    assert serializer.is_valid()
    assert serializer.validated_data["paid_days"] == paid_days


def test_not_fill_paid_days(user):
    """Test not fill paid days."""
    input_data = {
        "from_date": _date_strftime(date(CURRENT_YEAR, 2, 3)),
        "to_date": _date_strftime(date(CURRENT_YEAR, 2, 10)),
        "comment": "test",
        "reason": str(WorkBreakReason.VACATION),
        "user": user.pk,
        "paid_days": 30,
    }

    serializer = InputSerializer(data=input_data)

    assert serializer.is_valid()
    assert serializer.validated_data["paid_days"] == 30


def _date_strftime(date):
    """
    Date strftime.

    :param date:
    """
    return date.strftime(GITLAB_DATE_FORMAT)
