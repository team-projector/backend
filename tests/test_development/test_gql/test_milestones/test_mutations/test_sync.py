from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied
from jnt_django_graphene_toolbox.errors.permission_denied import ACCESS_DENIED

from apps.development.models.milestone import Milestone, MilestoneState
from tests.test_development.factories import ProjectGroupMilestoneFactory
from tests.test_development.factories.gitlab import GlGroupMilestoneFactory
from tests.test_development.test_gl.helpers import gl_mock, initializers
from tests.test_users.factories.gitlab import GlUserFactory
from tests.test_users.factories.user import UserFactory

KEY_ID = "id"


def test_query(make_group_manager, gql_client, gl_mocker, user, gql_raw):
    """
    Test query.

    :param make_group_manager:
    :param gql_client:
    :param gl_mocker:
    :param user:
    """
    group, gl_group = initializers.init_group()
    milestone = _prepare_sync_data(gl_mocker, group, gl_group)

    make_group_manager(group, user)
    assert milestone.state == MilestoneState.ACTIVE

    gql_client.set_user(user)
    response = gql_client.execute(
        gql_raw("sync_milestone"),
        variable_values={KEY_ID: milestone.pk},
    )

    assert "errors" not in response

    dto = response["data"]["syncMilestone"]["milestone"]
    assert dto[KEY_ID] == str(milestone.id)

    milestone.refresh_from_db()
    assert milestone.state == MilestoneState.CLOSED


def test_project_milestone(
    user,
    ghl_auth_mock_info,
    sync_milestone_mutation,
    gl_mocker,
    make_group_manager,
):
    """
    Test project milestone.

    :param user:
    :param ghl_auth_mock_info:
    :param sync_milestone_mutation:
    :param gl_mocker:
    :param make_group_manager:
    """
    group, gl_project = initializers.init_project()
    gl_milestone = GlGroupMilestoneFactory.create(state=MilestoneState.CLOSED)

    gl_assignee = GlUserFactory.create()
    UserFactory.create(gl_id=gl_assignee[KEY_ID])

    gl_mock.register_user(gl_mocker, gl_assignee)
    gl_mock.mock_project_endpoints(
        gl_mocker,
        gl_project,
        milestones=[gl_milestone],
    )

    milestone = ProjectGroupMilestoneFactory.create(
        gl_id=gl_milestone[KEY_ID],
        owner=group,
        state=MilestoneState.ACTIVE,
    )
    make_group_manager(group, user)

    assert milestone.state == MilestoneState.ACTIVE

    sync_milestone_mutation(
        root=None,
        info=ghl_auth_mock_info,
        id=milestone.id,
    )

    milestone.refresh_from_db()
    assert milestone.state == MilestoneState.CLOSED


def test_without_access(
    user,
    ghl_auth_mock_info,
    sync_milestone_mutation,
):
    """
    Test without access.

    :param user:
    :param ghl_auth_mock_info:
    :param sync_milestone_mutation:
    """
    milestone = ProjectGroupMilestoneFactory()

    resolve = sync_milestone_mutation(
        root=None,
        info=ghl_auth_mock_info,
        id=milestone.id,
    )

    assert isinstance(resolve, GraphQLPermissionDenied)
    assert resolve.extensions == {"code": ACCESS_DENIED}


def _prepare_sync_data(gl_mocker, group, gl_group) -> Milestone:
    gl_milestone = GlGroupMilestoneFactory.create(state=MilestoneState.CLOSED)

    gl_assignee = GlUserFactory.create()
    UserFactory.create(gl_id=gl_assignee[KEY_ID])

    gl_mock.register_user(gl_mocker, gl_assignee)
    gl_mock.mock_group_endpoints(
        gl_mocker,
        gl_group,
        milestones=[gl_milestone],
    )

    return ProjectGroupMilestoneFactory.create(
        gl_id=gl_milestone[KEY_ID],
        owner=group,
        state=MilestoneState.ACTIVE,
    )
