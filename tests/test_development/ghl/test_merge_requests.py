from apps.core.utils.time import seconds
from apps.development.models import TeamMember
from apps.development.graphql.types.merge_request import MergeRequestType
from apps.development.models import MergeRequest
from tests.test_development.factories import (
    IssueFactory,
    LabelFactory,
    MergeRequestFactory,
    TeamFactory,
    TeamMemberFactory,
)
from tests.test_development.factories_gitlab import AttrDict
from tests.test_users.factories import UserFactory


def test_merge_requests(user, client):
    MergeRequestFactory.create_batch(2, user=user)

    user_2 = UserFactory.create()
    MergeRequestFactory.create_batch(3, user=user_2)

    team = TeamFactory.create()
    TeamMemberFactory.create(user=user, team=team,
                             roles=TeamMember.roles.LEADER)
    TeamMemberFactory.create(user=user_2, team=team,
                             roles=TeamMember.roles.DEVELOPER)

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    merge_requests = MergeRequestType().get_queryset(
        MergeRequest.objects.all(), info
    )

    assert merge_requests.count() == 5


def test_merge_requests_not_teamlead(user, client):
    MergeRequestFactory.create_batch(2, user=user)

    user_2 = UserFactory.create()
    MergeRequestFactory.create_batch(3, user=user_2)

    team = TeamFactory.create()
    TeamMemberFactory.create(user=user, team=team,
                             roles=TeamMember.roles.DEVELOPER)
    TeamMemberFactory.create(user=user_2, team=team,
                             roles=TeamMember.roles.DEVELOPER)

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    merge_requests = MergeRequestType().get_queryset(
        MergeRequest.objects.all(), info
    )

    assert merge_requests.count() == 2
    assert all(item.user == user for item in merge_requests) is True


def test_metrics(user):
    merge_request = MergeRequestFactory.create(
        user=user,
        total_time_spent=seconds(hours=1),
        time_estimate=seconds(hours=2)
    )

    metrics = MergeRequestType.resolve_metrics(merge_request, None)
    assert metrics.remains == seconds(hours=1)


def test_resolve_participants(user, client):
    merge_request = MergeRequestFactory.create(user=user)

    user_1 = UserFactory.create()
    user_2 = UserFactory.create()
    merge_request.participants.add(user_1, user_2)

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    participants = MergeRequestType.resolve_participants(merge_request, info)

    assert participants.count() == 2
    assert set(participants.all()) == {user_1, user_2}


def test_resolve_labels(user, client):
    merge_request = MergeRequestFactory.create(user=user)

    label_1 = LabelFactory.create()
    label_2 = LabelFactory.create()
    merge_request.labels.add(label_1, label_2)

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    labels = MergeRequestType.resolve_labels(merge_request, info)

    assert labels.count() == 2
    assert set(labels.all()) == {label_1, label_2}


def test_resolve_issues(user, client):
    merge_request = MergeRequestFactory.create(user=user)

    issue_1 = IssueFactory.create()
    issue_2 = IssueFactory.create()
    merge_request.issues.add(issue_1, issue_2)

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    issues = MergeRequestType.resolve_issues(merge_request, info)

    assert issues.count() == 2
    assert set(issues.all()) == {issue_1, issue_2}
