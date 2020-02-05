# -*- coding: utf-8 -*-

from apps.payroll.models.work_break import WorkBreak
from tests.test_payroll.factories import WorkBreakFactory

GHL_QUERY_DELETE_WORK_BREAK = """
mutation ($id: ID!) {
  deleteWorkBreak(id: $id) {
    ok
  }
}
"""


def test_query(user, ghl_client):
    """Test delete raw query."""
    ghl_client.set_user(user)

    work_break = WorkBreakFactory.create(user=user)

    response = ghl_client.execute(
        GHL_QUERY_DELETE_WORK_BREAK,
        variables={"id": work_break.id},
    )

    assert response["data"]["deleteWorkBreak"]["ok"]
    assert not WorkBreak.objects.filter(id=work_break.id).exists()
