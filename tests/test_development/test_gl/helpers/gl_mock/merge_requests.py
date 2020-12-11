from tests.test_development.factories.gitlab import GlTimeStats

KEY_ID = "id"
KEY_IID = "iid"


def register_merge_request(mocker, project, merge_request):
    """
    Register merge request.

    :param mocker:
    :param project:
    :param merge_request:
    """
    mocker.register_get(
        "/projects/{0}/merge_requests/{1}".format(
            project[KEY_ID],
            merge_request[KEY_IID],
        ),
        merge_request,
    )


def register_merge_request_participants(
    mocker,
    project,
    merge_request,
    participants,
):
    """
    Register merge request participants.

    :param mocker:
    :param project:
    :param merge_request:
    :param participants:
    """
    mocker.register_get(
        "/projects/{0}/merge_requests/{1}/participants".format(
            project[KEY_ID],
            merge_request[KEY_IID],
        ),
        participants,
    )


def register_merge_request_time_stats(mocker, project, merge_request, stats):
    """
    Register merge request time stats.

    :param mocker:
    :param project:
    :param merge_request:
    :param stats:
    """
    mocker.register_get(
        "/projects/{0}/merge_requests/{1}/time_stats".format(
            project[KEY_ID],
            merge_request[KEY_IID],
        ),
        stats,
    )


def register_merge_request_labels(mocker, project, merge_request, labels):
    """
    Register merge request labels.

    :param mocker:
    :param project:
    :param merge_request:
    :param labels:
    """
    mocker.register_get(
        "/projects/{0}/merge_requests/{1}/labels".format(
            project[KEY_ID],
            merge_request[KEY_IID],
        ),
        labels,
    )


def register_merge_request_notes(mocker, project, merge_request, notes):
    """
    Register merge request notes.

    :param mocker:
    :param project:
    :param merge_request:
    :param notes:
    """
    mocker.register_get(
        "/projects/{0}/merge_requests/{1}/notes".format(
            project[KEY_ID],
            merge_request[KEY_IID],
        ),
        notes,
    )


def mock_merge_request_endpoints(mocker, project, merge_request, **kwargs):
    """
    Mock merge request endpoints.

    :param mocker:
    :param project:
    :param merge_request:
    """
    register_merge_request(mocker, project, merge_request)
    register_merge_request(mocker, project, merge_request)
    register_merge_request_time_stats(
        mocker,
        project,
        merge_request,
        kwargs.get("time_stats", GlTimeStats.create()),
    )
    register_merge_request_labels(
        mocker,
        project,
        merge_request,
        kwargs.get("labels", []),
    )
    register_merge_request_notes(
        mocker,
        project,
        merge_request,
        kwargs.get("notes", []),
    )
    register_merge_request_participants(
        mocker,
        project,
        merge_request,
        kwargs.get("participants", []),
    )
