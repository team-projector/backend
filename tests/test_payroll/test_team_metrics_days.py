from datetime import datetime, timedelta
from typing import Dict

from django.db.models import Sum
from django.test import override_settings
from django.utils import timezone
from pytest import raises

from apps.core.utils.time import seconds
from apps.development.models import TeamMember
from apps.development.models.issue import ISSUE_STATES
from apps.development.services.team.metrics.progress import (
    get_progress_metrics,
)
from apps.development.services.team.metrics.progress.base import (
    ProgressMetricsProvider,
)
from tests.helpers.base import format_date
from tests.test_development.factories import (
    IssueFactory,
    TeamFactory,
    TeamMemberFactory,
)
from tests.test_payroll.factories import IssueSpentTimeFactory
from tests.test_users.factories.user import UserFactory


@override_settings(TP_WEEKENDS_DAYS=[])
def test_simple(user):
    developer = UserFactory.create()
    issue = IssueFactory.create(user=developer,
                                due_date=datetime.now())

    team = TeamFactory.create()
    TeamMemberFactory.create(team=team, user=developer,
                             roles=TeamMember.roles.DEVELOPER)
    TeamMemberFactory.create(team=team, user=user,
                             roles=TeamMember.roles.LEADER)

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=4),
        user=developer,
        base=issue,
        time_spent=seconds(hours=3)
    )
    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=2, hours=5),
        user=developer,
        base=issue,
        time_spent=seconds(hours=2)
    )
    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=1),
        user=developer,
        base=issue,
        time_spent=seconds(hours=4)
    )
    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=1, hours=5),
        user=developer,
        base=issue,
        time_spent=-seconds(hours=3)
    )

    issue.time_estimate = seconds(hours=15)
    issue.total_time_spent = issue.time_spents.aggregate(
        spent=Sum("time_spent"),
    )["spent"]
    issue.state = ISSUE_STATES.OPENED
    issue.due_date = timezone.now() + timedelta(days=1)
    issue.save()

    start = timezone.now().date() - timedelta(days=5)
    end = timezone.now().date() + timedelta(days=5)
    metrics = get_progress_metrics(team, start, end, "day")

    assert len(metrics) == 2

    developer_metrics = next(
        item.metrics for item in metrics if item.user == developer)

    assert len(developer_metrics) == (end - start).days + 1

    _check_metrics(developer_metrics,
                   {
                       timezone.now() - timedelta(days=4): timedelta(
                           hours=3),
                       timezone.now() - timedelta(days=2): timedelta(
                           hours=2),
                       timezone.now() - timedelta(days=1): timedelta(
                           hours=1),
                   }, {
                       timezone.now(): timedelta(hours=8),
                       timezone.now() + timedelta(days=1): timedelta(
                           hours=1),
                   }, {
                       timezone.now() + timedelta(days=1): 1
                   }, {
                       timezone.now() + timedelta(days=1): timedelta(
                           hours=15)
                   }, {
                       timezone.now() + timedelta(days=1):
                           timedelta(
                               seconds=issue.time_estimate - issue.total_time_spent)
                   })


@override_settings(TP_WEEKENDS_DAYS=[])
def test_negative_remains(user):
    developer = UserFactory.create()
    issue = IssueFactory.create(user=developer,
                                due_date=datetime.now())

    team = TeamFactory.create()
    TeamMemberFactory.create(team=team, user=developer,
                             roles=TeamMember.roles.DEVELOPER)
    TeamMemberFactory.create(team=team, user=user,
                             roles=TeamMember.roles.LEADER)

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=4, hours=5),
        user=developer,
        base=issue,
        time_spent=seconds(hours=3)
    )

    issue.time_estimate = seconds(hours=2)
    issue.total_time_spent = issue.time_spents.aggregate(
        spent=Sum("time_spent"),
    )["spent"]
    issue.state = ISSUE_STATES.OPENED
    issue.due_date = timezone.now() + timedelta(days=1)
    issue.save()

    start = timezone.now().date() - timedelta(days=5)
    end = timezone.now().date() + timedelta(days=5)
    metrics = get_progress_metrics(team, start, end, "day")

    assert len(metrics) == 2

    developer_metrics = next(
        item.metrics for item in metrics if item.user == developer)

    assert len(developer_metrics) == (end - start).days + 1

    _check_metrics(developer_metrics,
                   {
                       timezone.now() - timedelta(days=4): timedelta(
                           hours=3),
                   }, {}, {
                       timezone.now() + timedelta(days=1): 1
                   }, {
                       timezone.now() + timedelta(days=1): timedelta(
                           hours=2)
                   }, {})


@override_settings(TP_WEEKENDS_DAYS=[])
def test_loading_day_already_has_spends(user):
    developer = UserFactory.create()
    issue = IssueFactory.create(user=developer,
                                due_date=datetime.now())

    team = TeamFactory.create()
    TeamMemberFactory.create(team=team, user=developer,
                             roles=TeamMember.roles.DEVELOPER)
    TeamMemberFactory.create(team=team, user=user,
                             roles=TeamMember.roles.LEADER)

    issue_2 = IssueFactory.create(user=developer,
                                  state=ISSUE_STATES.OPENED,
                                  total_time_spent=timedelta(
                                      hours=3).total_seconds(),
                                  time_estimate=timedelta(
                                      hours=10).total_seconds())

    IssueSpentTimeFactory.create(
        date=timezone.now(),
        user=developer,
        base=issue_2,
        time_spent=seconds(hours=1)
    )
    IssueSpentTimeFactory.create(
        date=timezone.now(),
        user=developer,
        base=issue_2,
        time_spent=seconds(hours=2)
    )
    IssueSpentTimeFactory.create(
        date=timezone.now(),
        user=developer,
        base=issue,
        time_spent=seconds(hours=3)
    )

    issue.time_estimate = int(seconds(hours=4))
    issue.total_time_spent = int(seconds(hours=3))
    issue.state = ISSUE_STATES.OPENED
    issue.due_date = timezone.now()
    issue.save()

    issue_2.total_time_spent = issue_2.time_spents.aggregate(
        spent=Sum("time_spent"),
    )["spent"]
    issue_2.save()

    start = timezone.now().date() - timedelta(days=5)
    end = timezone.now().date() + timedelta(days=5)
    metrics = get_progress_metrics(team, start, end, "day")

    assert len(metrics) == 2

    developer_metrics = next(
        item.metrics for item in metrics if item.user == developer)

    assert len(developer_metrics) == (end - start).days + 1

    _check_metrics(developer_metrics,
                   {
                       timezone.now(): timedelta(hours=6)
                   }, {
                       timezone.now(): timedelta(hours=8),
                       timezone.now() + timedelta(days=1): timedelta(
                           hours=6),
                   }, {
                       timezone.now(): 1,
                   }, {
                       timezone.now(): timedelta(hours=4),
                   }, {
                       timezone.now(): timedelta(
                           seconds=issue.time_estimate - issue.total_time_spent)
                   })


@override_settings(TP_WEEKENDS_DAYS=[])
def test_not_in_range(user):
    developer = UserFactory.create()
    issue = IssueFactory.create(user=developer,
                                due_date=datetime.now())

    team = TeamFactory.create()
    TeamMemberFactory.create(team=team, user=developer,
                             roles=TeamMember.roles.DEVELOPER)
    TeamMemberFactory.create(team=team, user=user,
                             roles=TeamMember.roles.LEADER)

    issue.time_estimate = 0
    issue.total_time_spent = 0
    issue.state = ISSUE_STATES.OPENED
    issue.save()

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=5, hours=5),
        user=developer,
        base=issue,
        time_spent=seconds(hours=2)
    )
    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=1),
        user=developer,
        base=issue,
        time_spent=seconds(hours=4)
    )
    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=1, hours=5),
        user=developer,
        base=issue,
        time_spent=-seconds(hours=3)
    )
    IssueSpentTimeFactory.create(
        date=timezone.now() + timedelta(days=1),
        user=developer,
        base=issue,
        time_spent=seconds(hours=3)
    )

    start = timezone.now().date() - timedelta(days=3)
    end = timezone.now().date() + timedelta(days=3)
    metrics = get_progress_metrics(team, start, end, "day")

    developer_metrics = next(
        item.metrics
        for item in metrics
        if item.user == developer
    )

    assert len(developer_metrics) == (end - start).days + 1

    _check_metrics(developer_metrics,
                   {
                       timezone.now() - timedelta(days=1): timedelta(
                           hours=1),
                       timezone.now() + timedelta(days=1): timedelta(
                           hours=3)
                   }, {}, {
                       timezone.now(): 1
                   }, {}, {})


@override_settings(TP_WEEKENDS_DAYS=[])
def test_another_user_not_in_team(user):
    developer = UserFactory.create()
    issue = IssueFactory.create(user=developer,
                                due_date=datetime.now())

    team = TeamFactory.create()
    TeamMemberFactory.create(team=team, user=developer,
                             roles=TeamMember.roles.DEVELOPER)
    TeamMemberFactory.create(team=team, user=user,
                             roles=TeamMember.roles.LEADER)

    issue.time_estimate = 0
    issue.total_time_spent = 0
    issue.state = ISSUE_STATES.OPENED
    issue.save()

    another_user = UserFactory.create()

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=2, hours=5),
        user=developer,
        base=issue,
        time_spent=seconds(hours=2)
    )
    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=1),
        user=another_user,
        base=issue,
        time_spent=seconds(hours=4)
    )
    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=1, hours=5),
        user=developer,
        base=issue,
        time_spent=-seconds(hours=3)
    )
    IssueSpentTimeFactory.create(
        date=timezone.now() + timedelta(days=1),
        user=another_user,
        base=issue,
        time_spent=seconds(hours=3)
    )

    start = timezone.now().date() - timedelta(days=5)
    end = timezone.now().date() + timedelta(days=5)
    metrics = get_progress_metrics(team, start, end, "day")

    assert len(metrics) == 2
    assert any(item.user == another_user for item in metrics) is False


@override_settings(TP_WEEKENDS_DAYS=[])
def test_another_user_in_team(user):
    developer = UserFactory.create()
    issue = IssueFactory.create(user=developer,
                                due_date=datetime.now())

    team = TeamFactory.create()
    TeamMemberFactory.create(team=team, user=developer,
                             roles=TeamMember.roles.DEVELOPER)
    TeamMemberFactory.create(team=team, user=user,
                             roles=TeamMember.roles.LEADER)

    another_user = UserFactory.create()
    TeamMemberFactory.create(team=team, user=another_user,
                             roles=TeamMember.roles.DEVELOPER)

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=2, hours=3),
        user=developer,
        base=issue,
        time_spent=seconds(hours=2)
    )
    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=1),
        user=another_user,
        base=issue,
        time_spent=seconds(hours=4)
    )
    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=1, hours=5),
        user=developer,
        base=issue,
        time_spent=-seconds(hours=3)
    )
    IssueSpentTimeFactory.create(
        date=timezone.now() + timedelta(days=1),
        user=another_user,
        base=issue,
        time_spent=seconds(hours=3)
    )

    issue.time_estimate = seconds(hours=4)
    issue.total_time_spent = 0
    issue.state = ISSUE_STATES.OPENED
    issue.save()
    issue.save()

    start = timezone.now().date() - timedelta(days=5)
    end = timezone.now().date() + timedelta(days=5)
    metrics = get_progress_metrics(team, start, end, "day")

    assert len(metrics) == 3

    developer_metrics = next(
        item.metrics for item in metrics if item.user == developer)

    assert len(developer_metrics) == (end - start).days + 1

    _check_metrics(developer_metrics,
                   {
                       timezone.now() - timedelta(days=2,
                                                  hours=3): timedelta(
                           hours=2),
                       timezone.now() - timedelta(days=1,
                                                  hours=3): -timedelta(
                           hours=3),
                   }, {
                       timezone.now(): timedelta(hours=4),
                   }, {
                       timezone.now(): 1,
                   }, {
                       timezone.now(): timedelta(hours=4),
                   }, {
                       timezone.now(): timedelta(hours=4),
                   })

    another_user_metrics = next(
        item.metrics
        for item in metrics
        if item.user == another_user
    )

    assert len(another_user_metrics) == (end - start).days + 1

    _check_metrics(another_user_metrics,
                   {
                       timezone.now() - timedelta(days=1,
                                                  hours=3): timedelta(
                           hours=4),
                       timezone.now() + timedelta(days=1): timedelta(
                           hours=3),
                   }, {}, {}, {}, {})


def test_bad_group(db):
    with raises(ValueError):
        get_progress_metrics(
            TeamFactory.create(),
            timezone.now().date() - timedelta(days=5),
            timezone.now().date() + timedelta(days=5),
            "test_bad_group"
        )


def test_provider_not_implemented(user):
    with raises(NotImplementedError):
        ProgressMetricsProvider(
            TeamFactory.create(),
            datetime.now().date() - timedelta(days=5),
            datetime.now().date() + timedelta(days=5),
        ).get_user_metrics(user)


def _check_metrics(
    metrics,
    spents: Dict[datetime, timedelta],
    loadings: Dict[datetime, timedelta],
    issues_counts: Dict[datetime, int],
    time_estimates: Dict[datetime, timedelta],
    time_remains: Dict[datetime, timedelta],
    planned_work_hours: int = 8,
):
    spents = _prepare_metrics(spents)
    loadings = _prepare_metrics(loadings)
    time_estimates = _prepare_metrics(time_estimates)
    issues_counts = _prepare_metrics(issues_counts)
    time_remains = _prepare_metrics(time_remains)

    for metric in metrics:
        assert metric.start == metric.end
        assert metric.planned_work_hours == planned_work_hours

        _check_metric(metric, "time_spent", spents)
        _check_metric(metric, "time_estimate", time_estimates)
        _check_metric(metric, "loading", loadings)
        _check_metric(metric, "time_remains", time_remains)

        if str(metric.start) in issues_counts:
            assert metric.issues_count == issues_counts.get(str(metric.start))
        else:
            assert metric.issues_count == 0


def _prepare_metrics(metrics):
    return {
        format_date(d): time
        for d, time in metrics.items()
    }


def _check_metric(metric, metric_name, values):
    dt = str(metric.start)

    if dt in values:
        assert getattr(metric, metric_name) == values.get(dt).total_seconds()
    else:
        assert getattr(metric, metric_name) == 0
