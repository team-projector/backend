from django.utils import timezone

from apps.development.graphql.filters.projects import (
    ProjectsFilterSet, MILESTONE_DUE_DATE_SORT
)
from apps.development.models import Project
from tests.test_development.factories import ProjectMilestoneFactory


def test_sort_by_milestone(user, client):
    projs = []
    for n in range(3):
        m = ProjectMilestoneFactory()
        ProjectMilestoneFactory(
            owner=m.owner,
            due_date=timezone.now()
        )
        ProjectMilestoneFactory(
            owner=m.owner,
            due_date=timezone.now() + timezone.timedelta(days=n)
        )

        projs.append(m.owner)

    results = ProjectsFilterSet(
        data={'order_by': MILESTONE_DUE_DATE_SORT},
        queryset=Project.objects
    ).qs

    assert [projs[0].id, projs[1].id, projs[2].id] == [p.id for p in results]

    results = ProjectsFilterSet(
        data={'order_by': f'-{MILESTONE_DUE_DATE_SORT}'},
        queryset=Project.objects
    ).qs

    assert [projs[2].id, projs[1].id, projs[0].id] == [p.id for p in results]
