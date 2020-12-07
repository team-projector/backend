from jnt_django_graphene_toolbox.errors import (
    GraphQLInputError,
    GraphQLPermissionDenied,
)

from tests.test_development.factories import IssueFactory


def test_without_permissions(
    user,
    ghl_auth_mock_info,
    update_ticket_mutation,
    ticket,
):
    """Test non project manager."""
    resolve = update_ticket_mutation(
        root=None,
        info=ghl_auth_mock_info,
        id=ticket.id,
        title="new_{0}".format(ticket.title),
    )

    isinstance(resolve, GraphQLPermissionDenied)


def test_both_params_attach_and_issues(
    project_manager,
    ghl_auth_mock_info,
    update_ticket_mutation,
    ticket,
):
    """Test both attach and rewrite issues."""
    issue = IssueFactory(user=project_manager)

    resolve = update_ticket_mutation(
        root=None,
        info=ghl_auth_mock_info,
        id=ticket.pk,
        issues=[issue.pk],
        attach_issues=[issue.pk],
    )

    isinstance(resolve, GraphQLInputError)

    extensions = resolve.extensions  # noqa: WPS441
    assert len(extensions["fieldErrors"]) == 1
    assert extensions["fieldErrors"][0]["fieldName"] == "nonFieldErrors"
