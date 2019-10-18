from apps.development.models import Issue, TeamMember
from apps.development.models.project_member import PROJECT_MEMBER_ROLES
from tests.test_development.factories import (
    IssueFactory,
    ProjectFactory,
    ProjectMemberFactory,
    TeamFactory,
    TeamMemberFactory,
)
from tests.test_users.factories import UserFactory


def test_by_assignee(user):
    another_user = UserFactory.create()

    IssueFactory.create_batch(4, user=user)
    IssueFactory.create_batch(2, user=another_user)

    allowed = Issue.objects.allowed_for_user(user)

    assert allowed.count() == 4


def test_by_team_leader(user):
    leader = UserFactory.create()
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=leader,
        team=team,
        roles=TeamMember.roles.leader
    )

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.developer
    )

    IssueFactory.create_batch(4, user=user)

    allowed = Issue.objects.allowed_for_user(leader)

    assert allowed.count() == 4


def test_by_team_leader_and_user(user):
    leader = UserFactory.create()
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=leader,
        team=team,
        roles=TeamMember.roles.leader
    )

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.developer
    )

    IssueFactory.create_batch(4, user=user)
    IssueFactory.create_batch(3, user=leader)

    allowed = Issue.objects.allowed_for_user(leader)

    assert allowed.count() == 7


def test_by_team_watcher(user):
    watcher = UserFactory.create()
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=watcher,
        team=team,
        roles=TeamMember.roles.watcher
    )

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.developer
    )

    IssueFactory.create_batch(4, user=user)

    allowed = Issue.objects.allowed_for_user(watcher)

    assert allowed.count() == 4


def test_by_project_manager(db):
    project_1 = ProjectFactory.create()
    pm_1 = ProjectMemberFactory.create(
        role=PROJECT_MEMBER_ROLES.project_manager,
        owner=project_1,
    )

    issue_1 = IssueFactory.create(project=project_1)
    issue_2 = IssueFactory.create(project=project_1)

    project_2 = ProjectFactory.create()
    pm_2 = ProjectMemberFactory.create(
        role=PROJECT_MEMBER_ROLES.project_manager,
        owner=project_2,
    )

    issue_3 = IssueFactory.create(project=project_2)
    issue_4 = IssueFactory.create(project=project_2)

    project_3 = ProjectFactory.create()
    pm_3 = ProjectMemberFactory.create(
        role=PROJECT_MEMBER_ROLES.developer,
        owner=project_3,
    )

    IssueFactory.create_batch(3, project=project_3)

    project_4 = ProjectFactory.create()
    pm_4 = ProjectMemberFactory.create(
        role=PROJECT_MEMBER_ROLES.customer,
        owner=project_4,
    )

    IssueFactory.create_batch(3, project=project_4)

    allowed = Issue.objects.allowed_for_user(pm_1.user)

    assert allowed.count() == 2
    assert set(allowed) == {issue_1, issue_2}

    allowed = Issue.objects.allowed_for_user(pm_2.user)

    assert allowed.count() == 2
    assert set(allowed) == {issue_3, issue_4}

    allowed = Issue.objects.allowed_for_user(pm_3.user)

    assert allowed.count() == 0

    allowed = Issue.objects.allowed_for_user(pm_4.user)

    assert allowed.count() == 0


def test_by_project_manager_and_another_project(user):
    project_1 = ProjectFactory.create()
    pm = ProjectMemberFactory.create(
        user=user,
        role=PROJECT_MEMBER_ROLES.project_manager,
        owner=project_1,
    )

    issue_1 = IssueFactory.create(project=project_1)
    issue_2 = IssueFactory.create(project=project_1)

    project_2 = ProjectFactory.create()

    TeamMemberFactory.create(
        user=pm.user,
        team=TeamFactory.create(),
        roles=TeamMember.roles.developer
    )

    issue_3 = IssueFactory.create(project=project_2, user=pm.user)
    issue_4 = IssueFactory.create(project=project_2, user=pm.user)

    IssueFactory.create_batch(5, project=project_2)

    allowed = Issue.objects.allowed_for_user(pm.user)

    assert allowed.count() == 4
    assert set(allowed) == {issue_1, issue_2, issue_3, issue_4}
