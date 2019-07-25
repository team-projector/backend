from datetime import datetime

from apps.development.graphql.resolvers import resolve_issues_summary
from tests.test_development.factories import IssueFactory
from tests.test_development.factories_gitlab import AttrDict


def test_one_user(user):
    IssueFactory.create_batch(
        5, user=user,
        total_time_spent=0,
        due_date=datetime.now()
    )

    info = AttrDict({
        'context': AttrDict({
            'user': user
        })
    })

    results = resolve_issues_summary(None, info=info, user=user.id)

    _check_summary(results, 5, 0, 0)


def _check_summary(data, issues_count, time_spent, problems_count):
    assert data.issues_count == issues_count
    assert data.time_spent == time_spent
    assert data.problems_count == problems_count
