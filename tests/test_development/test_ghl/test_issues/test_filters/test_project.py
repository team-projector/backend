# -*- coding: utf-8 -*-

from apps.development.graphql.filters import IssuesFilterSet
from apps.development.models.issue import Issue
from tests.test_development.factories import IssueFactory, ProjectFactory


def test_by_project(user):
    project = ProjectFactory.create()

    IssueFactory.create(user=user, project=project)
    IssueFactory.create_batch(3, user=user)

    results = IssuesFilterSet(
        data={"project": project.pk},
        queryset=Issue.objects.all(),
    ).qs

    assert results.count() == 1
    assert results.first().project == project
