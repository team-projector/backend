# -*- coding: utf-8 -*-

from apps.development.services.merge_request.gl.manager import (
    MergeRequestGlManager,
)
from tests.test_development.test_gl.helpers import (
    gl_checkers,
    gl_mock,
    initializers,
)
from tests.test_users.factories.gitlab import GlUserFactory


def test_participants(db, gl_mocker, gl_client):
    project, gl_project = initializers.init_project()
    merge_request, gl_merge_request = initializers.init_merge_request(
        project,
        gl_project,
    )
    gl_participants = GlUserFactory.create_batch(2)

    for to_register in gl_participants:
        gl_mock.register_user(gl_mocker, to_register)

    gl_mock.mock_project_endpoints(
        gl_mocker,
        gl_project,
        merge_requests=[gl_merge_request],
    )
    gl_mock.mock_merge_request_endpoints(
        gl_mocker,
        gl_project,
        gl_merge_request,
        participants=gl_participants,
    )

    gl_project = gl_client.projects.get(id=project.gl_id)
    gl_merge_request = gl_project.mergerequests.get(id=merge_request.gl_iid)

    MergeRequestGlManager().sync_participants(merge_request, gl_merge_request)

    for gl_participant in gl_participants:
        participant = merge_request.participants.get(
            login=gl_participant['username'],
        )
        gl_checkers.check_user(participant, gl_participant)
