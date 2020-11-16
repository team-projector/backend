from apps.payroll.models.work_break import WorkBreak
from tests.test_payroll.factories import WorkBreakFactory


def test_query(user, ghl_client, ghl_raw):
    """Test delete raw query."""
    ghl_client.set_user(user)

    work_break = WorkBreakFactory.create(user=user)

    response = ghl_client.execute(
        ghl_raw("delete_work_break"),
        variable_values={"id": work_break.id},
    )

    assert response["data"]["deleteWorkBreak"]["ok"]
    assert not WorkBreak.objects.filter(id=work_break.id).exists()
