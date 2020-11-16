from datetime import date

from apps.core.gitlab import GITLAB_DATE_FORMAT
from apps.users.models import User
from tests.test_payroll.factories import SalaryFactory, WorkBreakFactory
from tests.test_users.factories import UserFactory


def test_raw_query(user, ghl_client, ghl_raw):
    """Test getting all users raw query."""
    UserFactory.create(roles=0)
    ghl_client.set_user(user)

    response = ghl_client.execute(ghl_raw("all_users"))

    assert "errors" not in response
    assert response["data"]["users"]["count"] == 1
    assert User.objects.count() == 2


def test_success(user, ghl_auth_mock_info, all_users_query):
    """Test success getting users."""
    UserFactory.create(is_active=False)

    response = all_users_query(root=None, info=ghl_auth_mock_info)

    assert len(response.edges) == 1
    assert response.edges[0].node == user


def test_metrics_some_users(user, ghl_client, ghl_raw):
    """Test getting all users raw query."""
    user1 = UserFactory.create()

    salary = SalaryFactory.create(
        payed=True,
        created_by=user,
        user=user,
        period_to=date(2020, 10, 10),
    )
    salary1 = SalaryFactory.create(
        payed=True,
        created_by=user,
        user=user1,
        period_to=date(2020, 10, 15),
    )

    work_break = WorkBreakFactory.create(paid_days=3, user=user, paid=True)
    work_break1 = WorkBreakFactory.create(paid_days=5, user=user1, paid=True)

    ghl_client.set_user(user)
    response = ghl_client.execute(ghl_raw("all_users"))

    assert "errors" not in response

    user_nodes = response["data"]["users"]["edges"]
    assert len(user_nodes) == 2

    user_node = _get_user_node(user, user_nodes)
    user_node1 = _get_user_node(user1, user_nodes)

    _check_user_metrics(user_node, salary, work_break)
    _check_user_metrics(user_node1, salary1, work_break1)


def _check_user_metrics(user_node, salary, work_break):
    metrics = user_node["metrics"]

    assert metrics["lastSalaryDate"] == salary.period_to.strftime(
        GITLAB_DATE_FORMAT,
    )
    assert metrics["paidWorkBreaksDays"] == work_break.paid_days


def _get_user_node(user, user_nodes):
    filtered = [
        node["node"]
        for node in user_nodes
        if node["node"]["id"] == str(user.pk)
    ]

    return filtered[0]
