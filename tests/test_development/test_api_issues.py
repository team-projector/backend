from django.urls import resolve
from rest_framework import status

from apps.development.models import TeamMember
from apps.development.rest.views import IssuesViewset
from tests.test_development.factories import (
    FeatureFactory, IssueFactory, ProjectGroupMilestoneFactory,
    TeamFactory, TeamMemberFactory)
from tests.test_users.factories import UserFactory


def test_issues_api_path():
    resolver = resolve('/api/issues')

    assert resolver.url_name == 'issues-list'
    assert resolver.func.cls == IssuesViewset

    resolver = resolve('/api/issues/1')

    assert resolver.url_name == 'issues-detail'
    assert resolver.func.cls == IssuesViewset
    assert resolver.kwargs == {'pk': '1'}


def test_list(user, client):
    view = IssuesViewset.as_view(actions={'get': 'list'})

    IssueFactory.create_batch(5, user=user)

    client.set_credentials(user)
    response = view(client.get('/'))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 5


def test_retrieve(user, client):
    view = IssuesViewset.as_view(actions={'get': 'retrieve'})

    issue = IssueFactory.create(user=user)

    client.set_credentials(user)
    response = view(client.get('/'), pk=issue.id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == issue.id


def test_retrieve_not_found(user, client):
    view = IssuesViewset.as_view(actions={'get': 'retrieve'})

    issue = IssueFactory.create(user=user)

    client.set_credentials(user)
    response = view(client.get('/'), pk=issue.id + 1)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_issue_feature(user, client):
    view = IssuesViewset.as_view(actions={'patch': 'partial_update'})

    issue = IssueFactory.create(user=user)
    feature = FeatureFactory.create(
        milestone=ProjectGroupMilestoneFactory.create())

    assert issue.feature_id != feature.id

    client.set_credentials(user)
    response = view(
        client.patch('/', {'feature': feature.id}),
        pk=issue.id
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data['feature']['id'] == feature.id


def test_update_issue_feature_not_exist(user, client):
    view = IssuesViewset.as_view(actions={'patch': 'partial_update'})

    issue = IssueFactory.create(user=user)

    client.set_credentials(user)
    response = view(
        client.patch('/', {'feature': 0}),
        pk=issue.id
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_change_issue_feature(user, client):
    view = IssuesViewset.as_view(actions={'patch': 'partial_update'})

    issue = IssueFactory.create(
        user=user,
        feature=FeatureFactory.create(
            milestone=ProjectGroupMilestoneFactory.create()
        )
    )
    feature = FeatureFactory.create(
        milestone=ProjectGroupMilestoneFactory.create()
    )

    assert feature.id != issue.feature_id

    client.set_credentials(user)
    response = view(
        client.patch('/', {'feature': feature.id}),
        pk=issue.id
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data['feature']['id'] == feature.id


def test_show_participants(user, client):
    view = IssuesViewset.as_view(actions={'get': 'list'})

    user_2 = UserFactory.create()

    team = TeamFactory.create()
    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.leader
    )

    TeamMemberFactory.create(
        user=user_2,
        team=team,
        roles=TeamMember.roles.developer
    )

    issue = IssueFactory.create(user=user_2)

    users = UserFactory.create_batch(size=3)
    issue.participants.set(users)

    client.set_credentials(user)
    response = view(client.get('/'), {'user': user_2.id})

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1
    assert set(
        x['id'] for x in response.data['results'][0]['participants']
    ) == set(x.id for x in users)


def test_show_users(user, client):
    view = IssuesViewset.as_view(actions={'get': 'list'})

    user_2 = UserFactory.create()

    team = TeamFactory.create()
    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.leader
    )

    TeamMemberFactory.create(
        user=user_2,
        team=team,
        roles=TeamMember.roles.developer
    )

    IssueFactory.create(user=user_2)
    IssueFactory.create(user=user)

    client.set_credentials(user)
    response = view(client.get('/'))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 2
    assert set(x['user']['id'] for x in response.data['results']) == \
           {user.id, user_2.id}


def test_issues_filter_by_team_empty(user, client):
    view = IssuesViewset.as_view(actions={'get': 'list'})

    user_1 = UserFactory.create()
    user_2 = UserFactory.create()

    team_1 = TeamFactory.create()
    team_2 = TeamFactory.create()

    team_1.members.set([user_1, user_2])
    team_2.members.add(user_2)

    IssueFactory.create(user=user)

    client.set_credentials(user)
    response = view(client.get('/', {'team': team_1.id}))

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_issues_filter_by_team_watcher_empty(user, client):
    view = IssuesViewset.as_view(actions={'get': 'list'})

    user_1 = UserFactory.create()

    team_1 = TeamFactory.create()
    team_2 = TeamFactory.create()

    team_1.members.set([user_1, user])
    team_2.members.add(user)

    TeamMember.objects.filter(
        team=team_1
    ).update(
        roles=TeamMember.roles.watcher
    )

    IssueFactory.create(user=user)

    client.set_credentials(user)
    response = view(client.get('/', {'team': team_1.id}))

    assert response.status_code == status.HTTP_200_OK

    response_ids = [x['id'] for x in response.data['results']]
    response_ids.sort()

    assert response_ids == []


def test_issues_filter_by_team_leader(user, client):
    view = IssuesViewset.as_view(actions={'get': 'list'})

    user_1 = UserFactory.create()

    team_1 = TeamFactory.create()

    team_1.members.set([user_1, user])

    TeamMember.objects.filter(
        user=user_1, team=team_1
    ).update(
        roles=TeamMember.roles.leader
    )
    TeamMember.objects.filter(
        user=user, team=team_1
    ).update(
        roles=TeamMember.roles.watcher
    )

    issue_1 = IssueFactory.create(user=user_1)
    IssueFactory.create(user=user)

    client.set_credentials(user)
    response = view(client.get('/', {'team': team_1.id}))

    assert response.status_code == status.HTTP_200_OK

    results_ids = [x.id for x in [issue_1]]
    results_ids.sort()

    response_ids = [x['id'] for x in response.data['results']]
    response_ids.sort()

    assert results_ids == response_ids
