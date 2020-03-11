# -*- coding: utf-8 -*-

from http import HTTPStatus


def register_groups(mocker, groups):
    mocker.register_get("/groups", groups)


def register_group(mocker, group, status_code: int = HTTPStatus.OK):
    mocker.register_get(
        "/groups/{0}".format(group["id"]), group, status_code=status_code,
    )


def register_group_milestones(mocker, group, milestones):
    mocker.register_get(
        "/groups/{0}/milestones".format(group["id"]), milestones,
    )


def register_group_projects(mocker, group, projects):
    mocker.register_get(
        "/groups/{0}/projects".format(group["id"]), projects,
    )


def mock_group_endpoints(mocker, group, **kwargs):
    register_group(mocker, group)
    register_group_milestones(mocker, group, kwargs.get("milestones", []))
    register_group_projects(mocker, group, kwargs.get("projects", []))
