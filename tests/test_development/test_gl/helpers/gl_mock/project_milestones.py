# -*- coding: utf-8 -*-


def register_project_milestone(mocker, project, milestone):
    mocker.register_get(
        '/projects/{0}/milestones/{1}'.format(
            project['id'],
            milestone['id']
        ),
        milestone,
    )


def mock_project_milestone_endpoints(mocker, project, milestone, **kwargs):
    register_project_milestone(mocker, project, milestone)
