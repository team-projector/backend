# -*- coding: utf-8 -*-

import pytest

from apps.core.graphql.errors import GraphQLPermissionDenied
from apps.development.graphql.filters import IssuesFilterSet
from apps.development.models.issue import Issue
from tests.test_development.factories import (
    IssueFactory,
    ProjectMilestoneFactory,
)


def test_filter_by_milestone(user, auth_rf):
    user.roles.PROJECT_MANAGER = True
    user.save()

    milestone = ProjectMilestoneFactory.create()
    IssueFactory.create_batch(3, user=user, milestone=milestone)

    IssueFactory.create_batch(
        2,
        user=user,
        milestone=ProjectMilestoneFactory.create(),
    )

    results = IssuesFilterSet(
        data={"milestone": milestone.pk},
        queryset=Issue.objects.all(),
        request=auth_rf.get("/"),
    ).qs

    assert results.count() == 3
    assert all(item.milestone == milestone for item in results)


def test_not_project_manager(user, auth_rf):
    milestone = ProjectMilestoneFactory.create()
    IssueFactory.create_batch(3, user=user, milestone=milestone)

    with pytest.raises(GraphQLPermissionDenied):
        IssuesFilterSet(  # noqa: WPS428
            data={"milestone": milestone.pk},
            queryset=Issue.objects.all(),
            request=auth_rf.get("/")
        ).qs
