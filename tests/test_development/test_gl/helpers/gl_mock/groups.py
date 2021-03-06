from http import HTTPStatus

KEY_ID = "id"


def register_groups(mocker, groups):
    """
    Register groups.

    :param mocker:
    :param groups:
    """
    mocker.register_get("/groups", groups)


def register_group(mocker, group, status_code: int = HTTPStatus.OK):
    """
    Register group.

    :param mocker:
    :param group:
    :param status_code:
    :type status_code: int, defaults to HTTPStatus.OK
    """
    mocker.register_get(
        "/groups/{0}".format(group[KEY_ID]),
        group,
        status_code=status_code,
    )


def register_group_milestones(mocker, group, milestones):
    """
    Register group milestones.

    :param mocker:
    :param group:
    :param milestones:
    """
    mocker.register_get(
        "/groups/{0}/milestones".format(group[KEY_ID]),
        milestones,
    )
    for milestone in milestones:
        mocker.register_get(
            "/groups/{0}/milestones/{1}".format(
                group[KEY_ID],
                milestone[KEY_ID],
            ),
            milestone,
        )


def register_group_projects(mocker, group, projects):
    """
    Register group projects.

    :param mocker:
    :param group:
    :param projects:
    """
    mocker.register_get(
        "/groups/{0}/projects".format(group[KEY_ID]),
        projects,
    )


def mock_group_endpoints(mocker, group, **kwargs):
    """
    Mock group endpoints.

    :param mocker:
    :param group:
    """
    register_group(mocker, group)
    register_group_milestones(mocker, group, kwargs.get("milestones", []))
    register_group_projects(mocker, group, kwargs.get("projects", []))
