# -*- coding: utf-8 -*-

from http import HTTPStatus


def register_project(mocker, project, status_code: int = HTTPStatus.OK):
    mocker.register_get(
        "/projects/{0}".format(project["id"]),
        project,
        status_code=status_code,
    )


def register_project_hooks(mocker, project, hooks):
    mocker.register_get("/projects/{0}/hooks".format(project["id"]), hooks)


def register_create_project_hook(mocker, project, response):
    mocker.register_post("/projects/{0}/hooks".format(project["id"]), response)


def register_delete_project_hook(mocker, project):
    mocker.register_delete("/projects/{0}/hooks".format(project["id"]))


def register_project_labels(mocker, project, labels):
    mocker.register_get("/projects/{0}/labels".format(project["id"]), labels)


def register_project_issues(mocker, project, issues):
    mocker.register_get("/projects/{0}/issues".format(project["id"]), issues)


def register_project_milestones(mocker, project, milestones):
    mocker.register_get(
        "/projects/{0}/milestones".format(project["id"]),
        milestones,
    )


def register_project_merge_requests(mocker, project, merge_requests):
    mocker.register_get(
        "/projects/{0}/merge_requests".format(project["id"]),
        merge_requests,
    )


def mock_project_endpoints(mocker, project, **kwargs):
    register_project(mocker, project)
    register_project_issues(mocker, project, kwargs.get("issues", []))
    register_project_labels(mocker, project, kwargs.get("labels", []))
    register_project_milestones(mocker, project, kwargs.get("milestones", []))
    register_project_hooks(mocker, project, kwargs.get("hooks", []))
    register_project_merge_requests(
        mocker,
        project,
        kwargs.get("merge_requests", []),
    )
