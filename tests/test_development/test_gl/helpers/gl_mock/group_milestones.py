# -*- coding: utf-8 -*-


def register_group_milestone(mocker, group, milestone):
    mocker.register_get(
        "/groups/{0}/milestones/{1}".format(group["id"], milestone["id"]),
        milestone,
    )


def mock_group_milestone_endpoints(mocker, group, milestone, **kwargs):
    register_group_milestone(mocker, group, milestone)
