from tests.test_development.factories.gitlab import GlTimeStats

KEY_ID = "id"
KEY_IID = "iid"


def register_issue(mocker, project, issue):
    """
    Register issue.

    :param mocker:
    :param project:
    :param issue:
    """
    mocker.register_get(
        "/projects/{0}/issues/{1}".format(project[KEY_ID], issue[KEY_IID]),
        issue,
    )


def register_issue_participants(mocker, project, issue, participants):
    """
    Register issue participants.

    :param mocker:
    :param project:
    :param issue:
    :param participants:
    """
    mocker.register_get(
        "/projects/{0}/issues/{1}/participants".format(
            project[KEY_ID],
            issue[KEY_IID],
        ),
        participants,
    )


def register_issue_notes(mocker, project, issue, notes):
    """
    Register issue notes.

    :param mocker:
    :param project:
    :param issue:
    :param notes:
    """
    mocker.register_get(
        "/projects/{0}/issues/{1}/notes".format(
            project[KEY_ID],
            issue[KEY_IID],
        ),
        notes,
    )


def register_issue_labels(mocker, project, issue, labels):
    """
    Register issue labels.

    :param mocker:
    :param project:
    :param issue:
    :param labels:
    """
    mocker.register_get(
        "/projects/{0}/issues/{1}/labels".format(
            project[KEY_ID],
            issue[KEY_IID],
        ),
        labels,
    )


def register_issue_time_stats(mocker, project, issue, stats):
    """
    Register issue time stats.

    :param mocker:
    :param project:
    :param issue:
    :param stats:
    """
    mocker.register_get(
        "/projects/{0}/issues/{1}/time_stats".format(
            project[KEY_ID],
            issue[KEY_IID],
        ),
        stats,
    )


def register_issue_closed_by(mocker, project, issue, closed_by):
    """
    Register issue closed by.

    :param mocker:
    :param project:
    :param issue:
    :param closed_by:
    """
    mocker.register_get(
        "/projects/{0}/issues/{1}/closed_by".format(
            project[KEY_ID],
            issue[KEY_IID],
        ),
        closed_by,
    )


def mock_issue_endpoints(mocker, project, issue, **kwargs):
    """
    Mock issue endpoints.

    :param mocker:
    :param project:
    :param issue:
    """
    register_issue(mocker, project, issue)
    register_issue_time_stats(
        mocker,
        project,
        issue,
        kwargs.get("time_stats", GlTimeStats.create()),
    )
    register_issue_notes(mocker, project, issue, kwargs.get("notes", []))
    register_issue_closed_by(
        mocker,
        project,
        issue,
        kwargs.get("closed_by", []),
    )
    register_issue_participants(
        mocker,
        project,
        issue,
        kwargs.get("participants", []),
    )
