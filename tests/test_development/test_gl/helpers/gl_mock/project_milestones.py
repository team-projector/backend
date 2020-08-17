# -*- coding: utf-8 -*-


def register_project_milestone(mocker, project, milestone):
    """
    Register project milestone.

    :param mocker:
    :param project:
    :param milestone:
    """
    mocker.register_get(
        "/projects/{0}/milestones/{1}".format(project["id"], milestone["id"]),
        milestone,
    )


def mock_project_milestone_endpoints(mocker, project, milestone, **kwargs):
    """
    Mock project milestone endpoints.

    :param mocker:
    :param project:
    :param milestone:
    """
    register_project_milestone(mocker, project, milestone)
