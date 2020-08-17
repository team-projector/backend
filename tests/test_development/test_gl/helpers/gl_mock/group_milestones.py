# -*- coding: utf-8 -*-


def register_group_milestone(mocker, group, milestone):
    """
    Register group milestone.

    :param mocker:
    :param group:
    :param milestone:
    """
    mocker.register_get(
        "/groups/{0}/milestones/{1}".format(group["id"], milestone["id"]),
        milestone,
    )


def mock_group_milestone_endpoints(mocker, group, milestone, **kwargs):
    """
    Mock group milestone endpoints.

    :param mocker:
    :param group:
    :param milestone:
    """
    register_group_milestone(mocker, group, milestone)
