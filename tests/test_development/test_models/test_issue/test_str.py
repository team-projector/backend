from tests.test_development.factories import IssueFactory


def test_issue(db):
    """
    Test issue.

    :param db:
    """
    issue = IssueFactory.create(title="issue_title_test")

    assert str(issue) == "issue_title_test"
