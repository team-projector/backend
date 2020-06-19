# -*- coding: utf-8 -*-

from datetime import datetime

from jnt_django_toolbox.helpers.objects import dict2obj

from apps.development.graphql.resolvers import resolve_issues_summary
from apps.development.graphql.resolvers.issues_summary import (
    resolve_issues_project_summaries,
    resolve_issues_team_summaries,
)
from apps.development.models import TeamMember
from apps.development.models.issue import Issue, IssueState
from tests.test_development.factories import (
    IssueFactory,
    ProjectFactory,
    TeamFactory,
    TeamMemberFactory,
)
from tests.test_development.test_services.test_issues.test_summary.helpers import (  # noqa: E501
    checkers,
)
from tests.test_users.factories.user import UserFactory


def test_issues_summary(user, ghl_auth_mock_info):
    IssueFactory.create_batch(
        5,
        user=user,
        state=IssueState.OPENED,
        total_time_spent=0,
        due_date=datetime.now(),
    )
    IssueFactory.create_batch(
        3, user=UserFactory.create(), state=IssueState.OPENED,
    )

    summary = resolve_issues_summary(
        parent=None, info=ghl_auth_mock_info, user=user.pk,
    )

    checkers.check_summary(summary, count=5, opened_count=5)


def test_issues_project_summaries(user):
    project = ProjectFactory()

    IssueFactory.create_batch(
        5,
        user=user,
        total_time_spent=300,
        time_estimate=400,
        project=project,
        due_date=datetime.now().date(),
    )

    issues = resolve_issues_project_summaries(
        dict2obj({"queryset": Issue.objects.all()}), None,
    )[0].issues

    assert issues.opened_count == 5
    assert issues.percentage == 1.0
    assert issues.remains == 500


def test_issues_team_summaries(user):
    team = TeamFactory.create()
    TeamMemberFactory.create(
        user=user, team=team, roles=TeamMember.roles.DEVELOPER,
    )
    IssueFactory.create_batch(
        5,
        user=user,
        total_time_spent=300,
        time_estimate=400,
        due_date=datetime.now().date(),
    )

    issues = resolve_issues_team_summaries(
        dict2obj({"queryset": Issue.objects.all()}), None,
    )[0].issues

    assert issues.opened_count == 5
    assert issues.percentage == 1.0
    assert issues.remains == 500
