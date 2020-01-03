# -*- coding: utf-8 -*-

from apps.development.models.note import NOTE_TYPES
from tests.test_development.factories import (
    IssueNoteFactory,
    LabelFactory,
    MergeRequestFactory,
    ProjectFactory,
    ProjectGroupFactory,
    ProjectMilestoneFactory,
    TeamFactory,
    TeamMemberFactory,
)
from tests.test_users.factories.user import UserFactory


def test_label(db):
    label = LabelFactory.create(title='label_title_test')

    assert str(label) == 'label_title_test'


def test_merge_request(db):
    merge_request = MergeRequestFactory.create(title='merge_request_title_test')

    assert str(merge_request) == 'merge_request_title_test'


def test_milestone(db):
    project = ProjectFactory.create(title='project_title_test')
    milestone = ProjectMilestoneFactory.create(
        title='milestone_title_test',
        owner=project,
    )

    assert str(milestone) == 'project_title_test / milestone_title_test'


def test_note(db):
    user = UserFactory.create(login='login_test')

    note = IssueNoteFactory.create(
        user=user,
        type=NOTE_TYPES.TIME_SPEND,
    )

    assert str(note) == f'login_test [{note.created_at}]: Time spend'


def test_project(db):
    project_1 = ProjectFactory.create(
        title='project_title_test',
        full_title='project_full_title_test',
    )
    project_2 = ProjectFactory.create(
        title='project_title_test',
        full_title=None,
    )

    assert str(project_1) == 'project_full_title_test'
    assert str(project_2) == 'project_title_test'


def test_group(db):
    group = ProjectGroupFactory.create(title='group_title_test')

    assert str(group) == 'group_title_test'


def test_team(db):
    team = TeamFactory.create(title='team_title_test')

    assert str(team) == 'team_title_test'


def test_teammember(db):
    user = UserFactory.create(login='login_test')

    team = TeamFactory.create(title='team_title_test')
    member = TeamMemberFactory.create(user=user, team=team)

    assert str(member) == 'team_title_test: login_test'
