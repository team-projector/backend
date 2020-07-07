# -*- coding: utf-8 -*-

from jnt_django_graphene_toolbox.errors import GraphQLInputError

from apps.development.models.milestone import MilestoneState
from tests.test_development.factories import ProjectGroupMilestoneFactory
from tests.test_development.factories.gitlab import GlGroupMilestoneFactory
from tests.test_development.test_gl.helpers import gl_mock, initializers
from tests.test_users.factories.gitlab import GlUserFactory
from tests.test_users.factories.user import UserFactory

GHL_QUERY_SYNC_MIELSTONE = """
mutation (
    $id: ID!
) {
syncMilestone(
    id: $id
) {
    milestone {
      id
      state
      glIid
      }
    }
  }
"""


def test_query(make_group_manager, ghl_client, gl_mocker, user):
    group, gl_group = initializers.init_group()
    gl_milestone = GlGroupMilestoneFactory.create(state=MilestoneState.CLOSED)

    gl_assignee = GlUserFactory.create()
    UserFactory.create(gl_id=gl_assignee["id"])

    gl_mock.register_user(gl_mocker, gl_assignee)
    gl_mock.mock_group_endpoints(
        gl_mocker, gl_group, milestones=[gl_milestone],
    )

    milestone = ProjectGroupMilestoneFactory.create(
        gl_id=gl_milestone["id"], owner=group, state=MilestoneState.ACTIVE,
    )
    make_group_manager(group, user)
    assert milestone.state == MilestoneState.ACTIVE

    ghl_client.set_user(user)
    response = ghl_client.execute(
        GHL_QUERY_SYNC_MIELSTONE, variable_values={"id": milestone.pk},
    )

    assert "errors" not in response

    dto = response["data"]["syncMilestone"]["milestone"]
    assert dto["id"] == str(milestone.id)

    milestone.refresh_from_db()
    assert milestone.state == MilestoneState.CLOSED


def test_project_milestone(
    user,
    ghl_auth_mock_info,
    sync_milestone_mutation,
    gl_mocker,
    make_group_manager,
):
    group, gl_project = initializers.init_project()
    gl_milestone = GlGroupMilestoneFactory.create(state=MilestoneState.CLOSED)

    gl_assignee = GlUserFactory.create()
    UserFactory.create(gl_id=gl_assignee["id"])

    gl_mock.register_user(gl_mocker, gl_assignee)
    gl_mock.mock_project_endpoints(
        gl_mocker, gl_project, milestones=[gl_milestone],
    )

    milestone = ProjectGroupMilestoneFactory.create(
        gl_id=gl_milestone["id"], owner=group, state=MilestoneState.ACTIVE,
    )
    make_group_manager(group, user)

    assert milestone.state == MilestoneState.ACTIVE

    sync_milestone_mutation(
        root=None, info=ghl_auth_mock_info, id=milestone.id,
    )

    milestone.refresh_from_db()
    assert milestone.state == MilestoneState.CLOSED


def test_without_access(
    user, ghl_auth_mock_info, sync_milestone_mutation,
):
    milestone = ProjectGroupMilestoneFactory()

    resolve = sync_milestone_mutation(
        root=None, info=ghl_auth_mock_info, id=milestone.id,
    )

    assert isinstance(resolve, GraphQLInputError)

    extensions = resolve.extensions  # noqa: WPS441
    assert len(extensions["fieldErrors"]) == 1
    assert extensions["fieldErrors"][0]["fieldName"] == "id"
