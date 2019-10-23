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


def test_by_project_manager_project_milestone(db):
    project_1 = ProjectFactory.create()
    pm_1 = ProjectMemberFactory.create(
        role=PROJECT_MEMBER_ROLES.project_manager,
        owner=project_1,
    )

    milestone_1 = ProjectMilestoneFactory.create(owner=project_1)

    issue_1 = IssueFactory.create(milestone=milestone_1)
    issue_2 = IssueFactory.create(milestone=milestone_1)

    project_2 = ProjectFactory.create()
    pm_2 = ProjectMemberFactory.create(
        role=PROJECT_MEMBER_ROLES.project_manager,
        owner=project_2,
    )

    milestone_2 = ProjectMilestoneFactory.create(owner=project_2)

    issue_3 = IssueFactory.create(milestone=milestone_2)
    issue_4 = IssueFactory.create(milestone=milestone_2)

    project_3 = ProjectFactory.create()
    pm_3 = ProjectMemberFactory.create(
        role=PROJECT_MEMBER_ROLES.developer,
        owner=project_3,
    )

    milestone_3 = ProjectMilestoneFactory.create(owner=project_3)

    IssueFactory.create_batch(3, milestone=milestone_3)

    project_4 = ProjectFactory.create()
    pm_4 = ProjectMemberFactory.create(
        role=PROJECT_MEMBER_ROLES.customer,
        owner=project_4,
    )

    milestone_4 = ProjectMilestoneFactory.create(owner=project_4)

    IssueFactory.create_batch(3, milestone=milestone_4)

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


def test_by_project_manager_group_milestone(db):
    group_1 = ProjectGroupFactory.create()
    pm_1 = ProjectMemberFactory.create(
        role=PROJECT_MEMBER_ROLES.project_manager,
        owner=group_1,
    )

    milestone_1 = ProjectGroupMilestoneFactory.create(owner=group_1)

    issue_1 = IssueFactory.create(milestone=milestone_1)
    issue_2 = IssueFactory.create(milestone=milestone_1)

    group_2 = ProjectGroupFactory.create()
    pm_2 = ProjectMemberFactory.create(
        role=PROJECT_MEMBER_ROLES.project_manager,
        owner=group_2,
    )

    milestone_2 = ProjectGroupMilestoneFactory.create(owner=group_2)

    issue_3 = IssueFactory.create(milestone=milestone_2)
    issue_4 = IssueFactory.create(milestone=milestone_2)

    group_3 = ProjectGroupFactory.create()
    pm_3 = ProjectMemberFactory.create(
        role=PROJECT_MEMBER_ROLES.developer,
        owner=group_3,
    )

    milestone_3 = ProjectGroupMilestoneFactory.create(owner=group_3)

    IssueFactory.create_batch(3, milestone=milestone_3)

    group_4 = ProjectGroupFactory.create()
    pm_4 = ProjectMemberFactory.create(
        role=PROJECT_MEMBER_ROLES.customer,
        owner=group_4,
    )

    milestone_4 = ProjectGroupMilestoneFactory.create(owner=group_4)

    IssueFactory.create_batch(3, milestone=milestone_4)

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


def test_by_project_manager_group_hier_milestone(db):
    group_level_3 = ProjectGroupFactory.create()
    pm_1 = ProjectMemberFactory.create(
        role=PROJECT_MEMBER_ROLES.project_manager,
        owner=group_level_3,
    )
    pm_2 = ProjectMemberFactory.create(
        role=PROJECT_MEMBER_ROLES.developer,
        owner=group_level_3,
    )

    milestone_1 = ProjectGroupMilestoneFactory.create(owner=group_level_3)

    issue_1 = IssueFactory.create(milestone=milestone_1)
    issue_2 = IssueFactory.create(milestone=milestone_1)

    group_level_2 = ProjectGroupFactory.create(parent=group_level_3)
    pm_3 = ProjectMemberFactory.create(
        role=PROJECT_MEMBER_ROLES.project_manager,
        owner=group_level_2,
    )

    milestone_2 = ProjectGroupMilestoneFactory.create(owner=group_level_2)

    issue_3 = IssueFactory.create(milestone=milestone_2)

    group_level_1 = ProjectGroupFactory.create(parent=group_level_2)

    milestone_3 = ProjectGroupMilestoneFactory.create(owner=group_level_1)

    issue_4 = IssueFactory.create(milestone=milestone_3)

    allowed = Issue.objects.allowed_for_user(pm_1.user)
    assert allowed.count() == 4
    assert set(allowed) == {issue_1, issue_2, issue_3, issue_4}

    allowed = Issue.objects.allowed_for_user(pm_2.user)
    assert allowed.count() == 0

    allowed = Issue.objects.allowed_for_user(pm_3.user)
    assert allowed.count() == 2
    assert set(allowed) == {issue_3, issue_4}


def test_project_members_team_members(db):
    user_pm = UserFactory.create()
    user_lead = UserFactory.create()
    user_dev = UserFactory.create()

    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=user_pm,
        team=team,
        roles=TeamMember.roles.watcher
    )
    TeamMemberFactory.create(
        user=user_lead,
        team=team,
        roles=TeamMember.roles.leader
    )
    TeamMemberFactory.create(
        user=user_dev,
        team=team,
        roles=TeamMember.roles.developer
    )

    project_1 = ProjectFactory.create()
    ProjectMemberFactory.create(
        user=user_pm,
        role=PROJECT_MEMBER_ROLES.project_manager,
        owner=project_1,
    )
    ProjectMemberFactory.create(
        user=user_lead,
        role=PROJECT_MEMBER_ROLES.developer,
        owner=project_1,
    )
    ProjectMemberFactory.create(
        user=user_dev,
        role=PROJECT_MEMBER_ROLES.developer,
        owner=project_1,
    )

    milestone_1 = ProjectMilestoneFactory.create(owner=project_1)

    issue_1 = IssueFactory.create(milestone=milestone_1, user=user_pm)
    issue_2 = IssueFactory.create(milestone=milestone_1, user=user_lead)
    issue_3 = IssueFactory.create(milestone=milestone_1, user=user_dev)
    issue_4 = IssueFactory.create(milestone=milestone_1, user=None)

    project_2 = ProjectFactory.create()
    ProjectMemberFactory.create(
        user=user_pm,
        role=PROJECT_MEMBER_ROLES.project_manager,
        owner=project_2,
    )
    ProjectMemberFactory.create(
        user=user_lead,
        role=PROJECT_MEMBER_ROLES.developer,
        owner=project_2,
    )
    ProjectMemberFactory.create(
        user=user_dev,
        role=PROJECT_MEMBER_ROLES.developer,
        owner=project_2,
    )

    milestone_2 = ProjectMilestoneFactory.create(owner=project_2)

    issue_5 = IssueFactory.create(milestone=milestone_2, user=user_dev)
    issue_6 = IssueFactory.create(milestone=milestone_2, user=user_dev)
    issue_7 = IssueFactory.create(milestone=milestone_2, user=None)

    project_3 = ProjectFactory.create()
    ProjectMemberFactory.create(
        user=user_lead,
        role=PROJECT_MEMBER_ROLES.developer,
        owner=project_3,
    )

    milestone_3 = ProjectMilestoneFactory.create(owner=project_3)

    IssueFactory.create_batch(10, milestone=milestone_3)

    allowed = Issue.objects.allowed_for_user(user_pm)

    assert allowed.count() == 7
    assert set(allowed) == {issue_1, issue_2, issue_3, issue_4, issue_5,
                            issue_6, issue_7}

    allowed = Issue.objects.allowed_for_user(user_lead)

    assert allowed.count() == 5
    assert set(allowed) == {issue_1, issue_2, issue_3, issue_5, issue_6}

    allowed = Issue.objects.allowed_for_user(user_dev)

    assert allowed.count() == 3
    assert set(allowed) == {issue_3, issue_5, issue_6}
