# -*- coding: utf-8 -*-

from tests.test_development.factories import IssueFactory, ProjectFactory
from tests.test_development.test_services.test_issues.test_allowed import (
    helpers,
)


def test_complex(
    project,
    team_watcher,
    team_leader,
    team_developer,
    make_project_manager,
    make_project_developer,
):
    make_project_manager(project, team_watcher)
    make_project_developer(project, team_leader)
    make_project_developer(project, team_developer)

    project2 = ProjectFactory.create()
    make_project_manager(project2, team_watcher)
    make_project_developer(project2, team_leader)
    make_project_developer(project2, team_developer)

    issues = [
        IssueFactory.create(project=project, user=team_watcher),
        IssueFactory.create(project=project, user=team_leader),
        IssueFactory.create(project=project, user=team_developer),
        IssueFactory.create(project=project, user=None),
        IssueFactory.create(project=project2, user=team_developer),
        IssueFactory.create(project=project2, user=team_developer),
        IssueFactory.create(project=project2, user=None),
    ]

    project3 = ProjectFactory.create()
    make_project_developer(project3, team_leader)

    IssueFactory.create_batch(10, project=project3)

    helpers.check_allowed_for_user(team_watcher, issues)
    helpers.check_allowed_for_user(team_leader, [
        issues[0],
        issues[1],
        issues[2],
        issues[4],
        issues[5],
    ])
    helpers.check_allowed_for_user(team_developer, [
        issues[2],
        issues[4],
        issues[5],
    ])