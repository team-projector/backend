# -*- coding: utf-8 -*-

from tests.test_development.factories import IssueFactory
from tests.test_payroll.factories import IssueSpentTimeFactory


def test_str(user):
    """
    Test str.

    :param user:
    """
    issue = IssueFactory.create(title="issue_title_test")
    spent_time = IssueSpentTimeFactory.create(
        user=user,
        time_spent=150,
        base=issue,
    )

    assert str(spent_time) == "{0} [issue_title_test]: 150".format(user.login)
