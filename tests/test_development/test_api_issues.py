from rest_framework import status

from apps.development.rest.views import IssuesViewset
from tests.test_development.factories import (
    FeatureFactory, IssueFactory, ProjectGroupMilestoneFactory,
)


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
