from tests.test_development.factories import (
    IssueFactory,
    ProjectFactory,
    ProjectGroupFactory,
    ProjectMemberFactory,
    TeamFactory,
    TeamMemberFactory,
)
from tests.test_users.factories.user import UserFactory

from apps.development.models import Issue, Project, ProjectGroup, TeamMember
from apps.development.models.project_member import PROJECT_MEMBER_ROLES


def test_tm_assignee(user):
    another_user = UserFactory.create()

    IssueFactory.create_batch(4, user=user)
    IssueFactory.create_batch(2, user=another_user)

    allowed = Issue.objects.allowed_for_user(user)

    assert allowed.count() == 4


def test_tm_leader(user):
    leader = UserFactory.create()
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=leader,
        team=team,
        roles=TeamMember.roles.LEADER
    )

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.DEVELOPER
    )

    IssueFactory.create_batch(4, user=user)

    allowed = Issue.objects.allowed_for_user(leader)

    assert allowed.count() == 4


def test_tm_leader_and_developer(user):
    leader = UserFactory.create()
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=leader,
        team=team,
        roles=TeamMember.roles.LEADER
    )

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.DEVELOPER
    )

    IssueFactory.create_batch(4, user=user)
    IssueFactory.create_batch(3, user=leader)

    allowed = Issue.objects.allowed_for_user(leader)

    assert allowed.count() == 7


def test_tm_watcher(user):
    watcher = UserFactory.create()
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=watcher,
        team=team,
        roles=TeamMember.roles.WATCHER
    )

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.DEVELOPER
    )

    IssueFactory.create_batch(4, user=user)

    allowed = Issue.objects.allowed_for_user(watcher)

    assert allowed.count() == 4


def test_pm_manager_projects(db):
    project_1 = ProjectFactory.create()
    manager = ProjectMemberFactory.create(
        role=PROJECT_MEMBER_ROLES.PROJECT_MANAGER,
        owner=project_1,
    )

    issue_1 = IssueFactory.create(project=project_1)
    issue_2 = IssueFactory.create(project=project_1)

    project_2 = ProjectFactory.create()
    ProjectMemberFactory.create(
        user=manager.user,
        role=PROJECT_MEMBER_ROLES.PROJECT_MANAGER,
        owner=project_2,
    )

    issue_3 = IssueFactory.create(project=project_2)

    project_3 = ProjectFactory.create()
    IssueFactory.create_batch(5, project=project_3)

    allowed = Issue.objects.allowed_for_user(manager.user)

    assert allowed.count() == 3
    assert set(allowed) == {issue_1, issue_2, issue_3}


def test_pm_developer_projects(db):
    project = ProjectFactory.create()
    developer = ProjectMemberFactory.create(
        role=PROJECT_MEMBER_ROLES.DEVELOPER,
        owner=project,
    )

    IssueFactory.create_batch(5, project=project)

    allowed = Issue.objects.allowed_for_user(developer.user)

    assert allowed.count() == 0


def test_pm_customer_projects(db):
    project = ProjectFactory.create()
    customer = ProjectMemberFactory.create(
        role=PROJECT_MEMBER_ROLES.CUSTOMER,
        owner=project,
    )

    IssueFactory.create_batch(5, project=project)

    allowed = Issue.objects.allowed_for_user(customer.user)

    assert allowed.count() == 0


def test_pm_manager_groups(db):
    group_1 = ProjectGroupFactory.create()
    manager = ProjectMemberFactory.create(
        role=PROJECT_MEMBER_ROLES.PROJECT_MANAGER,
        owner=group_1,
    )
    project_1 = ProjectFactory.create(group=group_1)

    issue_1 = IssueFactory.create(project=project_1)
    issue_2 = IssueFactory.create(project=project_1)

    group_2 = ProjectGroupFactory.create()
    ProjectMemberFactory.create(
        user=manager.user,
        role=PROJECT_MEMBER_ROLES.PROJECT_MANAGER,
        owner=group_2,
    )
    project_2 = ProjectFactory.create(group=group_2)

    issue_3 = IssueFactory.create(project=project_2)

    group_3 = ProjectGroupFactory.create()
    project_3 = ProjectFactory.create(group=group_3)

    IssueFactory.create_batch(5, project=project_3)

    allowed = Issue.objects.allowed_for_user(manager.user)

    assert allowed.count() == 3
    assert set(allowed) == {issue_1, issue_2, issue_3}


def test_pm_developer_groups(db):
    group = ProjectGroupFactory.create()
    developer = ProjectMemberFactory.create(
        role=PROJECT_MEMBER_ROLES.DEVELOPER,
        owner=group,
    )
    project = ProjectFactory.create(group=group)

    IssueFactory.create_batch(5, project=project)

    allowed = Issue.objects.allowed_for_user(developer.user)

    assert allowed.count() == 0


def test_pm_customer_group(db):
    group = ProjectGroupFactory.create()
    customer = ProjectMemberFactory.create(
        role=PROJECT_MEMBER_ROLES.CUSTOMER,
        owner=group,
    )
    project = ProjectFactory.create(group=group)

    IssueFactory.create_batch(5, project=project)

    allowed = Issue.objects.allowed_for_user(customer.user)

    assert allowed.count() == 0


def test_pm_manager_group_hierarchy(db):
    group_level_1 = ProjectGroupFactory.create()

    manager_1 = ProjectMemberFactory.create(
        role=PROJECT_MEMBER_ROLES.PROJECT_MANAGER,
        owner=group_level_1,
    )
    project_1 = ProjectFactory.create(group=group_level_1)

    issue_1 = IssueFactory.create(project=project_1)
    issue_2 = IssueFactory.create(project=project_1)

    group_level_0 = ProjectGroupFactory.create(parent=group_level_1)
    project_2 = ProjectFactory.create(group=group_level_0)

    issue_3 = IssueFactory.create(project=project_2)

    group_another = ProjectGroupFactory.create()
    project_3 = ProjectFactory.create(group=group_another)

    IssueFactory.create_batch(5, project=project_3)

    allowed = Issue.objects.allowed_for_user(manager_1.user)
    assert allowed.count() == 3
    assert set(allowed) == {issue_1, issue_2, issue_3}


def test_pm_and_tm_complex(db):
    manager = UserFactory.create()
    leader = UserFactory.create()
    developer = UserFactory.create()

    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=manager,
        team=team,
        roles=TeamMember.roles.WATCHER
    )
    TeamMemberFactory.create(
        user=leader,
        team=team,
        roles=TeamMember.roles.LEADER
    )
    TeamMemberFactory.create(
        user=developer,
        team=team,
        roles=TeamMember.roles.DEVELOPER
    )

    project_1 = ProjectFactory.create()
    ProjectMemberFactory.create(
        user=manager,
        role=PROJECT_MEMBER_ROLES.PROJECT_MANAGER,
        owner=project_1,
    )
    ProjectMemberFactory.create(
        user=leader,
        role=PROJECT_MEMBER_ROLES.DEVELOPER,
        owner=project_1,
    )
    ProjectMemberFactory.create(
        user=developer,
        role=PROJECT_MEMBER_ROLES.DEVELOPER,
        owner=project_1,
    )

    issue_1 = IssueFactory.create(project=project_1, user=manager)
    issue_2 = IssueFactory.create(project=project_1, user=leader)
    issue_3 = IssueFactory.create(project=project_1, user=developer)
    issue_4 = IssueFactory.create(project=project_1, user=None)

    project_2 = ProjectFactory.create()
    ProjectMemberFactory.create(
        user=manager,
        role=PROJECT_MEMBER_ROLES.PROJECT_MANAGER,
        owner=project_2,
    )
    ProjectMemberFactory.create(
        user=leader,
        role=PROJECT_MEMBER_ROLES.DEVELOPER,
        owner=project_2,
    )
    ProjectMemberFactory.create(
        user=developer,
        role=PROJECT_MEMBER_ROLES.DEVELOPER,
        owner=project_2,
    )

    issue_5 = IssueFactory.create(project=project_2, user=developer)
    issue_6 = IssueFactory.create(project=project_2, user=developer)
    issue_7 = IssueFactory.create(project=project_2, user=None)

    project_3 = ProjectFactory.create()
    ProjectMemberFactory.create(
        user=leader,
        role=PROJECT_MEMBER_ROLES.DEVELOPER,
        owner=project_3,
    )

    IssueFactory.create_batch(10, project=project_3)

    allowed = Issue.objects.allowed_for_user(manager)

    assert allowed.count() == 7
    assert set(allowed) == {issue_1, issue_2, issue_3, issue_4, issue_5,
                            issue_6, issue_7}

    allowed = Issue.objects.allowed_for_user(leader)

    assert allowed.count() == 5
    assert set(allowed) == {issue_1, issue_2, issue_3, issue_5, issue_6}

    allowed = Issue.objects.allowed_for_user(developer)

    assert allowed.count() == 3
    assert set(allowed) == {issue_3, issue_5, issue_6}
