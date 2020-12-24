from apps.payroll.models.work_break import WorkBreak
from tests.test_payroll.factories import WorkBreakFactory


def test_query(user, gql_client, gql_raw):
    """Test delete raw query."""
    gql_client.set_user(user)

    work_break = WorkBreakFactory.create(user=user)

    response = gql_client.execute(
        gql_raw("delete_work_break"),
        variable_values={"id": work_break.id},
    )

    assert response["data"]["deleteWorkBreak"]["ok"]
    assert not WorkBreak.objects.filter(id=work_break.id).exists()
