from collections import namedtuple
from datetime import date

from apps.core.gitlab import GITLAB_DATE_FORMAT
from apps.users.models import User
from tests.test_payroll.factories import SalaryFactory, WorkBreakFactory
from tests.test_users.factories import UserFactory

UserPaidData = namedtuple("UserPaidData", ("user", "salary", "work_break"))


def test_raw_query(user, gql_client, ghl_raw):
    """Test getting all users raw query."""
    UserFactory.create(roles=0)
    gql_client.set_user(user)

    response = gql_client.execute(ghl_raw("all_users"))

    assert "errors" not in response
    assert response["data"]["users"]["count"] == 1
    assert User.objects.count() == 2


def test_success(user, ghl_auth_mock_info, all_users_query):
    """Test success getting users."""
    UserFactory.create(is_active=False)

    response = all_users_query(root=None, info=ghl_auth_mock_info)

    assert len(response.edges) == 1
    assert response.edges[0].node == user


def test_metrics_some_users(user, gql_client, ghl_raw):
    """Test getting all users raw query."""
    user_paid_data = _get_user_paid_data(date(2020, 10, 10), 3, user)
    user1_paid_data = _get_user_paid_data(date(2020, 10, 15), 5)

    gql_client.set_user(user)
    response = gql_client.execute(ghl_raw("all_users"))

    assert "errors" not in response

    user_nodes = response["data"]["users"]["edges"]
    assert len(user_nodes) == 2

    _check_user_metrics(
        _get_user_node(user, user_nodes),
        user_paid_data.salary,
        user_paid_data.work_break,
    )
    _check_user_metrics(
        _get_user_node(user1_paid_data.user, user_nodes),
        user1_paid_data.salary,
        user1_paid_data.work_break,
    )


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


def _get_user_paid_data(period_to, paid_days, user=None) -> UserPaidData:
    user = user or UserFactory.create()

    return UserPaidData(
        user,
        SalaryFactory.create(
            payed=True,
            created_by=user,
            user=user,
            period_to=period_to,
        ),
        WorkBreakFactory.create(paid_days=paid_days, user=user, paid=True),
    )
