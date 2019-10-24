from apps.development.models import Issue, TeamMember
from apps.development.models.project_member import PROJECT_MEMBER_ROLES
from tests.test_development.factories import (
    IssueFactory,
    ProjectFactory,
    ProjectMemberFactory,
    ProjectMilestoneFactory,
    ProjectGroupFactory,
    ProjectGroupMilestoneFactory,
    TeamFactory,
    TeamMemberFactory,
)
from tests.test_users.factories import UserFactory


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


def test_tm_leader_and_developer(user):
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


def test_tm_watcher(user):
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


def test_pm_manager_project(db):
    project = ProjectFactory.create()
    manager = ProjectMemberFactory.create(
        role=PROJECT_MEMBER_ROLES.project_manager,
        owner=project,
    )

    milestone_1 = ProjectMilestoneFactory.create(owner=project)
    issue_1 = IssueFactory.create(milestone=milestone_1)
    issue_2 = IssueFactory.create(milestone=milestone_1)

    milestone_2 = ProjectMilestoneFactory.create(owner=project)
    issue_3 = IssueFactory.create(milestone=milestone_2)

    milestone_3 = ProjectMilestoneFactory.create()
    IssueFactory.create_batch(5, milestone=milestone_3)

    allowed = Issue.objects.allowed_for_user(manager.user)

    assert allowed.count() == 3
    assert set(allowed) == {issue_1, issue_2, issue_3}


def test_pm_manager_projects(db):
    project_1 = ProjectFactory.create()
    manager = ProjectMemberFactory.create(
        role=PROJECT_MEMBER_ROLES.project_manager,
        owner=project_1,
    )

    project_2 = ProjectFactory.create()
    ProjectMemberFactory.create(
        user=manager.user,
        role=PROJECT_MEMBER_ROLES.project_manager,
        owner=project_2,
    )

    milestone_1 = ProjectMilestoneFactory.create(owner=project_1)
    issue_1 = IssueFactory.create(milestone=milestone_1)
    issue_2 = IssueFactory.create(milestone=milestone_1)

    milestone_2 = ProjectMilestoneFactory.create(owner=project_2)
    issue_3 = IssueFactory.create(milestone=milestone_2)

    milestone_3 = ProjectMilestoneFactory.create()
    IssueFactory.create_batch(5, milestone=milestone_3)

    allowed = Issue.objects.allowed_for_user(manager.user)

    assert allowed.count() == 3
    assert set(allowed) == {issue_1, issue_2, issue_3}


def test_pm_developer_project(db):
    project = ProjectFactory.create()
    developer = ProjectMemberFactory.create(
        role=PROJECT_MEMBER_ROLES.developer,
        owner=project,
    )

    milestone = ProjectMilestoneFactory.create(owner=project)
    IssueFactory.create_batch(5, milestone=milestone)

    allowed = Issue.objects.allowed_for_user(developer.user)

    assert allowed.count() == 0


def test_pm_customer_project(db):
    project = ProjectFactory.create()
    customer = ProjectMemberFactory.create(
        role=PROJECT_MEMBER_ROLES.customer,
        owner=project,
    )

    milestone = ProjectMilestoneFactory.create(owner=project)
    IssueFactory.create_batch(5, milestone=milestone)

    allowed = Issue.objects.allowed_for_user(customer.user)

    assert allowed.count() == 0


def test_pm_manager_group(db):
    group = ProjectGroupFactory.create()
    manager = ProjectMemberFactory.create(
        role=PROJECT_MEMBER_ROLES.project_manager,
        owner=group,
    )

    milestone_1 = ProjectGroupMilestoneFactory.create(owner=group)
    issue_1 = IssueFactory.create(milestone=milestone_1)
    issue_2 = IssueFactory.create(milestone=milestone_1)

    milestone_2 = ProjectGroupMilestoneFactory.create(owner=group)
    issue_3 = IssueFactory.create(milestone=milestone_2)

    milestone_3 = ProjectGroupMilestoneFactory.create()
    IssueFactory.create_batch(5, milestone=milestone_3)

    allowed = Issue.objects.allowed_for_user(manager.user)

    assert allowed.count() == 3
    assert set(allowed) == {issue_1, issue_2, issue_3}


def test_pm_manager_groups(db):
    group_1 = ProjectGroupFactory.create()
    manager = ProjectMemberFactory.create(
        role=PROJECT_MEMBER_ROLES.project_manager,
        owner=group_1,
    )

    group_2 = ProjectGroupFactory.create()
    ProjectMemberFactory.create(
        user=manager.user,
        role=PROJECT_MEMBER_ROLES.project_manager,
        owner=group_2,
    )

    milestone_1 = ProjectGroupMilestoneFactory.create(owner=group_1)
    issue_1 = IssueFactory.create(milestone=milestone_1)
    issue_2 = IssueFactory.create(milestone=milestone_1)

    milestone_2 = ProjectGroupMilestoneFactory.create(owner=group_2)
    issue_3 = IssueFactory.create(milestone=milestone_2)

    milestone_3 = ProjectGroupMilestoneFactory.create()
    IssueFactory.create_batch(5, milestone=milestone_3)

    allowed = Issue.objects.allowed_for_user(manager.user)

    assert allowed.count() == 3
    assert set(allowed) == {issue_1, issue_2, issue_3}


def test_pm_developer_group(db):
    group = ProjectGroupFactory.create()
    developer = ProjectMemberFactory.create(
        role=PROJECT_MEMBER_ROLES.developer,
        owner=group,
    )

    milestone = ProjectGroupMilestoneFactory.create(owner=group)
    IssueFactory.create_batch(5, milestone=milestone)

    allowed = Issue.objects.allowed_for_user(developer.user)

    assert allowed.count() == 0


def test_pm_customer_group(db):
    group = ProjectGroupFactory.create()
    customer = ProjectMemberFactory.create(
        role=PROJECT_MEMBER_ROLES.customer,
        owner=group,
    )

    milestone = ProjectGroupMilestoneFactory.create(owner=group)
    IssueFactory.create_batch(5, milestone=milestone)

    allowed = Issue.objects.allowed_for_user(customer.user)

    assert allowed.count() == 0


def test_pm_managers_group_hierarchy(db):
    group_level_2 = ProjectGroupFactory.create()
    manager_1 = ProjectMemberFactory.create(
        role=PROJECT_MEMBER_ROLES.project_manager,
        owner=group_level_2,
    )

    milestone_1 = ProjectGroupMilestoneFactory.create(owner=group_level_2)
    issue_1 = IssueFactory.create(milestone=milestone_1)
    issue_2 = IssueFactory.create(milestone=milestone_1)

    group_level_1 = ProjectGroupFactory.create(parent=group_level_2)
    manager_2 = ProjectMemberFactory.create(
        role=PROJECT_MEMBER_ROLES.project_manager,
        owner=group_level_1,
    )

    milestone_2 = ProjectGroupMilestoneFactory.create(owner=group_level_1)
    issue_3 = IssueFactory.create(milestone=milestone_2)

    group_level_0 = ProjectGroupFactory.create(parent=group_level_1)

    milestone_3 = ProjectGroupMilestoneFactory.create(owner=group_level_0)
    issue_4 = IssueFactory.create(milestone=milestone_3)

    IssueFactory.create_batch(3)

    allowed = Issue.objects.allowed_for_user(manager_1.user)
    assert allowed.count() == 4
    assert set(allowed) == {issue_1, issue_2, issue_3, issue_4}

    allowed = Issue.objects.allowed_for_user(manager_2.user)
    assert allowed.count() == 2
    assert set(allowed) == {issue_3, issue_4}


def test_complex(db):
    manager = UserFactory.create()
    leader = UserFactory.create()
    developer = UserFactory.create()

    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=manager,
        team=team,
        roles=TeamMember.roles.watcher
    )
    TeamMemberFactory.create(
        user=leader,
        team=team,
        roles=TeamMember.roles.leader
    )
    TeamMemberFactory.create(
        user=developer,
        team=team,
        roles=TeamMember.roles.developer
    )

    project_1 = ProjectFactory.create()
    ProjectMemberFactory.create(
        user=manager,
        role=PROJECT_MEMBER_ROLES.project_manager,
        owner=project_1,
    )
    ProjectMemberFactory.create(
        user=leader,
        role=PROJECT_MEMBER_ROLES.developer,
        owner=project_1,
    )
    ProjectMemberFactory.create(
        user=developer,
        role=PROJECT_MEMBER_ROLES.developer,
        owner=project_1,
    )

    milestone_1 = ProjectMilestoneFactory.create(owner=project_1)

    issue_1 = IssueFactory.create(milestone=milestone_1, user=manager)
    issue_2 = IssueFactory.create(milestone=milestone_1, user=leader)
    issue_3 = IssueFactory.create(milestone=milestone_1, user=developer)
    issue_4 = IssueFactory.create(milestone=milestone_1, user=None)

    project_2 = ProjectFactory.create()
    ProjectMemberFactory.create(
        user=manager,
        role=PROJECT_MEMBER_ROLES.project_manager,
        owner=project_2,
    )
    ProjectMemberFactory.create(
        user=leader,
        role=PROJECT_MEMBER_ROLES.developer,
        owner=project_2,
    )
    ProjectMemberFactory.create(
        user=developer,
        role=PROJECT_MEMBER_ROLES.developer,
        owner=project_2,
    )

    milestone_2 = ProjectMilestoneFactory.create(owner=project_2)

    issue_5 = IssueFactory.create(milestone=milestone_2, user=developer)
    issue_6 = IssueFactory.create(milestone=milestone_2, user=developer)
    issue_7 = IssueFactory.create(milestone=milestone_2, user=None)

    project_3 = ProjectFactory.create()
    ProjectMemberFactory.create(
        user=leader,
        role=PROJECT_MEMBER_ROLES.developer,
        owner=project_3,
    )

    milestone_3 = ProjectMilestoneFactory.create(owner=project_3)

    IssueFactory.create_batch(10, milestone=milestone_3)

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
