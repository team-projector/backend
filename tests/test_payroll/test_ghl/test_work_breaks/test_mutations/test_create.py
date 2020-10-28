from datetime import timedelta

from django.utils import timezone

from apps.core.gitlab import GITLAB_DATETIME_FORMAT
from apps.payroll.models.work_break import WorkBreak, WorkBreakReason

GHL_QUERY_CREATE_WORK_BREAK = """
mutation ($user: ID!, $fromDate: DateTime!, $toDate: DateTime!,
$reason: WorkBreakReason!, $comment: String!) {
  createWorkBreak(user: $user, fromDate: $fromDate, toDate: $toDate,
  reason: $reason, comment: $comment) {
    workBreak {
      user {
        id
        name
      }
      id
      comment
    }
  }
}
"""


def test_query(user, ghl_client):
    """Test create raw query."""
    ghl_client.set_user(user)

    create_variables = {
        "user": user.id,
        "fromDate": _date_strftime(timezone.now()),
        "toDate": _date_strftime(timezone.now() + timedelta(seconds=10)),
        "reason": WorkBreakReason.DAYOFF,
        "comment": "test comment",
    }

    response = ghl_client.execute(
        GHL_QUERY_CREATE_WORK_BREAK,
        variable_values=create_variables,
    )

    dto = response["data"]["createWorkBreak"]["workBreak"]

    assert WorkBreak.objects.count() == 1
    assert dto["comment"] == create_variables["comment"]
    assert dto["user"]["id"] == str(user.id)


def _date_strftime(date):
    """
    Date strftime.

    :param date:
    """
    return date.strftime(GITLAB_DATETIME_FORMAT)
