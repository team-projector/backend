from contextlib import suppress

from rest_framework import status

from apps.development.models import TeamMember
from tests.test_development.factories import (
    IssueFactory, TeamFactory, TeamMemberFactory
)
from tests.test_users.factories import UserFactory


def test_one_member(user, api_client):
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.leader
    )

    IssueFactory.create_batch(2, user=user)

    another_user = UserFactory.create()
    IssueFactory.create_batch(3, user=another_user)

    api_client.set_credentials(user)
    response = api_client.get('/api/issues', {
        'team': team.id
    })

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 2


def test_many_members(user, api_client):
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.leader
    )

    IssueFactory.create_batch(2, user=user)

    another_user = UserFactory.create()
    IssueFactory.create_batch(3, user=another_user)

    TeamMemberFactory.create(
        user=another_user,
        team=team,
        roles=TeamMember.roles.developer
    )

    api_client.set_credentials(user)
    response = api_client.get('/api/issues', {
        'team': team.id
    })

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 5


def test_many_teams(user, api_client):
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.leader
    )

    another_user = UserFactory.create()

    IssueFactory.create_batch(2, user=user)
    IssueFactory.create_batch(3, user=another_user)

    another_team = TeamFactory.create()
    TeamMemberFactory.create(
        user=user,
        team=another_team,
        roles=TeamMember.roles.watcher
    )

    TeamMemberFactory.create(
        user=another_user,
        team=another_team,
        roles=TeamMember.roles.developer
    )

    api_client.set_credentials(user)
    response = api_client.get('/api/issues', {
        'team': team.id
    })

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 2


def _get_issue_by_id(self, items, issue):
    with suppress(StopIteration):
        return next(item for item in items if item['id'] == issue.id)
