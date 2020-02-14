from datetime import date, datetime, timedelta
from typing import Dict

from django.db.models import Sum
from django.test import override_settings
from django.utils import timezone

from apps.core.utils.date import begin_of_week
from apps.core.utils.time import seconds
from apps.development.models import TeamMember
from apps.development.models.issue import ISSUE_STATES
from apps.development.services.team.metrics.progress import (
    get_progress_metrics,
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
    issue = IssueFactory.create(user=developer, due_date=datetime.now())

    team = TeamFactory.create()
    TeamMemberFactory.create(team=team, user=developer,
                             roles=TeamMember.roles.DEVELOPER)
    TeamMemberFactory.create(team=team, user=user,
                             roles=TeamMember.roles.LEADER)

    monday = begin_of_week(timezone.now().date())

    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=4),
        user=developer,
        base=issue,
        time_spent=seconds(hours=3)
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=2, hours=5),
        user=developer,
        base=issue,
        time_spent=seconds(hours=2)
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1),
        user=developer,
        base=issue,
        time_spent=seconds(hours=4)
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1, hours=5),
        user=developer,
        base=issue,
        time_spent=-seconds(hours=3)
    )

    issue.time_estimate = seconds(hours=15)
    issue.total_time_spent = issue.time_spents.aggregate(
        spent=Sum("time_spent"),
    )["spent"]
    issue.state = ISSUE_STATES.OPENED
    issue.due_date = monday + timedelta(days=1)
    issue.save()

    start = monday - timedelta(days=5)
    end = monday + timedelta(days=5)
    metrics = get_progress_metrics(team, start, end, "week")

    assert len(metrics) == 2

    developer_metrics = next(
        item.metrics for item in metrics if item.user == developer)

    assert len(developer_metrics) == 2

    _check_metrics(developer_metrics,
                   {
                       monday: timedelta(hours=6)
                   }, {
                       monday: 1
                   }, {
                       monday: timedelta(hours=15)
                   }, {})


@override_settings(TP_WEEKENDS_DAYS=[])
def test_efficiency_more_1(user):
    developer = UserFactory.create()
    issue = IssueFactory.create(user=developer,
                                due_date=datetime.now())

    team = TeamFactory.create()
    TeamMemberFactory.create(team=team, user=developer,
                             roles=TeamMember.roles.DEVELOPER)
    TeamMemberFactory.create(team=team, user=user,
                             roles=TeamMember.roles.LEADER)

    monday = begin_of_week(timezone.now().date())

    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=4),
        user=developer,
        base=issue,
        time_spent=seconds(hours=3)
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=2, hours=5),
        user=developer,
        base=issue,
        time_spent=seconds(hours=2)
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1),
        user=developer,
        base=issue,
        time_spent=seconds(hours=4)
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1, hours=5),
        user=developer,
        base=issue,
        time_spent=-seconds(hours=3)
    )

    issue.time_estimate = seconds(hours=15)
    issue.total_time_spent = issue.time_spents.aggregate(
        spent=Sum("time_spent")
    )["spent"]
    issue.state = ISSUE_STATES.CLOSED
    issue.due_date = monday + timedelta(days=1)
    issue.closed_at = monday + timedelta(days=1)
    issue.save()

    start = monday - timedelta(days=5)
    end = monday + timedelta(days=5)
    metrics = get_progress_metrics(team, start, end, "week")

    assert len(metrics) == 2

    developer_metrics = next(
        item.metrics for item in metrics if item.user == developer)

    assert len(developer_metrics) == 2

    _check_metrics(developer_metrics,
                   {
                       monday: timedelta(hours=6)
                   }, {
                       monday: 1
                   }, {
                       monday: timedelta(hours=15)
                   }, {
                       monday: issue.time_estimate / issue.total_time_spent
                   })


@override_settings(TP_WEEKENDS_DAYS=[])
def test_efficiency_less_1(user):
    developer = UserFactory.create()
    issue = IssueFactory.create(user=developer,
                                due_date=datetime.now())

    team = TeamFactory.create()
    TeamMemberFactory.create(team=team, user=developer,
                             roles=TeamMember.roles.DEVELOPER)
    TeamMemberFactory.create(team=team, user=user,
                             roles=TeamMember.roles.LEADER)

    monday = begin_of_week(timezone.now().date())

    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=4),
        user=developer,
        base=issue,
        time_spent=seconds(hours=3)
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=2, hours=5),
        user=developer,
        base=issue,
        time_spent=seconds(hours=2)
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1),
        user=developer,
        base=issue,
        time_spent=seconds(hours=4)
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1, hours=5),
        user=developer,
        base=issue,
        time_spent=-seconds(hours=3)
    )

    issue.time_estimate = seconds(hours=3)
    issue.total_time_spent = issue.time_spents.aggregate(
        spent=Sum("time_spent")
    )["spent"]
    issue.state = ISSUE_STATES.CLOSED
    issue.due_date = monday + timedelta(days=1)
    issue.closed_at = monday + timedelta(days=1)
    issue.save()

    start = monday - timedelta(days=5)
    end = monday + timedelta(days=5)
    metrics = get_progress_metrics(team, start, end, "week")

    developer_metrics = next(
        item.metrics for item in metrics if item.user == developer)

    assert len(developer_metrics) == 2

    _check_metrics(developer_metrics,
                   {
                       monday: timedelta(hours=6)
                   }, {
                       monday: 1
                   }, {
                       monday: timedelta(hours=3)
                   }, {
                       monday: issue.time_estimate / issue.total_time_spent
                   })


@override_settings(TP_WEEKENDS_DAYS=[])
def test_efficiency_zero_estimate(user):
    developer = UserFactory.create()
    issue = IssueFactory.create(user=developer,
                                due_date=datetime.now())

    team = TeamFactory.create()
    TeamMemberFactory.create(team=team, user=developer,
                             roles=TeamMember.roles.DEVELOPER)
    TeamMemberFactory.create(team=team, user=user,
                             roles=TeamMember.roles.LEADER)

    monday = begin_of_week(timezone.now().date())

    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=4),
        user=developer,
        base=issue,
        time_spent=seconds(hours=3)
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=2, hours=5),
        user=developer,
        base=issue,
        time_spent=seconds(hours=2)
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1),
        user=developer,
        base=issue,
        time_spent=seconds(hours=4)
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1, hours=5),
        user=developer,
        base=issue,
        time_spent=-seconds(hours=3)
    )

    issue.time_estimate = 0
    issue.total_time_spent = issue.time_spents.aggregate(
        spent=Sum("time_spent"),
    )["spent"]
    issue.state = ISSUE_STATES.CLOSED
    issue.due_date = monday + timedelta(days=1)
    issue.closed_at = monday + timedelta(days=1)
    issue.save()

    start = monday - timedelta(days=5)
    end = monday + timedelta(days=5)
    metrics = get_progress_metrics(team, start, end, "week")

    developer_metrics = next(
        item.metrics for item in metrics if item.user == developer)

    assert len(developer_metrics) == 2

    _check_metrics(developer_metrics,
                   {
                       monday: timedelta(hours=6)
                   }, {
                       monday: 1
                   }, {}, {})


@override_settings(TP_WEEKENDS_DAYS=[])
def test_efficiency_zero_spend(user):
    developer = UserFactory.create()
    issue = IssueFactory.create(user=developer,
                                due_date=datetime.now())

    team = TeamFactory.create()
    TeamMemberFactory.create(team=team, user=developer,
                             roles=TeamMember.roles.DEVELOPER)
    TeamMemberFactory.create(team=team, user=user,
                             roles=TeamMember.roles.LEADER)

    monday = begin_of_week(timezone.now().date())

    issue.time_estimate = seconds(hours=2)
    issue.total_time_spent = 0
    issue.state = ISSUE_STATES.CLOSED
    issue.due_date = monday + timedelta(days=1)
    issue.closed_at = monday + timedelta(days=1)
    issue.save()

    start = monday - timedelta(days=5)
    end = monday + timedelta(days=5)
    metrics = get_progress_metrics(team, start, end, "week")

    developer_metrics = next(
        item.metrics
        for item in metrics
        if item.user == developer
    )

    assert len(developer_metrics) == 2

    _check_metrics(developer_metrics,
                   {},
                   {
                       monday: 1
                   }, {
                       monday: timedelta(hours=2)
                   }, {})


@override_settings(TP_WEEKENDS_DAYS=[])
def test_many_weeks(user):
    developer = UserFactory.create()
    issue = IssueFactory.create(user=developer,
                                due_date=datetime.now())

    team = TeamFactory.create()
    TeamMemberFactory.create(team=team, user=developer,
                             roles=TeamMember.roles.DEVELOPER)
    TeamMemberFactory.create(team=team, user=user,
                             roles=TeamMember.roles.LEADER)

    monday = begin_of_week(timezone.now().date())

    IssueSpentTimeFactory.create(
        date=monday - timedelta(days=4),
        user=developer,
        base=issue,
        time_spent=seconds(hours=3)
    )
    IssueSpentTimeFactory.create(
        date=monday - timedelta(days=2, hours=5),
        user=developer,
        base=issue,
        time_spent=seconds(hours=2)
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1),
        user=developer,
        base=issue,
        time_spent=seconds(hours=4)
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1, hours=5),
        user=developer,
        base=issue,
        time_spent=-seconds(hours=3)
    )

    issue.time_estimate = seconds(hours=15)
    issue.total_time_spent = issue.time_spents.aggregate(
        spent=Sum("time_spent"),
    )["spent"]
    issue.state = ISSUE_STATES.OPENED
    issue.due_date = monday + timedelta(days=2)
    issue.save()

    start = monday - timedelta(days=5)
    end = monday + timedelta(days=5)
    metrics = get_progress_metrics(team, start, end, "week")

    developer_metrics = next(
        item.metrics for item in metrics if item.user == developer)

    assert len(developer_metrics) == 2

    _check_metrics(developer_metrics,
                   {
                       monday - timedelta(weeks=1): timedelta(hours=5),
                       monday: timedelta(hours=1)
                   }, {
                       monday: 1
                   }, {
                       monday: timedelta(hours=15)
                   }, {})


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

    monday = begin_of_week(timezone.now().date())

    IssueSpentTimeFactory.create(
        date=monday - timedelta(days=4),
        user=developer,
        base=issue,
        time_spent=seconds(hours=3)
    )
    IssueSpentTimeFactory.create(
        date=monday - timedelta(days=2, hours=5),
        user=developer,
        base=issue,
        time_spent=seconds(hours=2)
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1),
        user=developer,
        base=issue,
        time_spent=seconds(hours=4)
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1, hours=5),
        user=developer,
        base=issue,
        time_spent=-seconds(hours=3)
    )

    issue.time_estimate = seconds(hours=15)
    issue.total_time_spent = issue.time_spents.aggregate(
        spent=Sum("time_spent"),
    )["spent"]
    issue.state = ISSUE_STATES.OPENED
    issue.due_date = monday + timedelta(days=1)
    issue.save()

    start = monday
    end = monday + timedelta(weeks=1, days=5)
    metrics = get_progress_metrics(team, start, end, "week")

    developer_metrics = next(
        item.metrics
        for item in metrics
        if item.user == developer
    )

    assert len(developer_metrics) == 2

    _check_metrics(developer_metrics,
                   {
                       monday: timedelta(hours=1)
                   }, {
                       monday: 1
                   }, {
                       monday: timedelta(hours=15)
                   }, {})


@override_settings(TP_WEEKENDS_DAYS=[])
def test_another_user(user):
    developer = UserFactory.create()
    issue = IssueFactory.create(user=developer,
                                due_date=datetime.now())

    team = TeamFactory.create()
    TeamMemberFactory.create(team=team, user=developer,
                             roles=TeamMember.roles.DEVELOPER)
    TeamMemberFactory.create(team=team, user=user,
                             roles=TeamMember.roles.LEADER)

    another_user = UserFactory.create()

    monday = begin_of_week(timezone.now().date())

    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=4),
        user=developer,
        base=issue,
        time_spent=seconds(hours=3)
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=2, hours=5),
        user=developer,
        base=issue,
        time_spent=seconds(hours=2)
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1),
        user=another_user,
        base=issue,
        time_spent=seconds(hours=4)
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1, hours=5),
        user=another_user,
        base=issue,
        time_spent=-seconds(hours=3)
    )

    issue.time_estimate = seconds(hours=15)
    issue.total_time_spent = issue.time_spents.aggregate(
        spent=Sum("time_spent"),
    )["spent"]
    issue.state = ISSUE_STATES.OPENED
    issue.due_date = monday + timedelta(days=1)
    issue.save()

    start = monday - timedelta(days=5)
    end = monday + timedelta(days=5)
    metrics = get_progress_metrics(team, start, end, "week")

    developer_metrics = next(
        item.metrics for item in metrics if item.user == developer)

    assert len(developer_metrics) == 2

    _check_metrics(developer_metrics,
                   {
                       monday: timedelta(hours=5)
                   }, {
                       monday: 1
                   }, {
                       monday: timedelta(hours=15)
                   }, {})


@override_settings(TP_WEEKENDS_DAYS=[])
def test_many_issues(user):
    developer = UserFactory.create()
    issue = IssueFactory.create(user=developer,
                                due_date=datetime.now())

    team = TeamFactory.create()
    TeamMemberFactory.create(team=team, user=developer,
                             roles=TeamMember.roles.DEVELOPER)
    TeamMemberFactory.create(team=team, user=user,
                             roles=TeamMember.roles.LEADER)

    monday = begin_of_week(datetime.now().date())
    another_issue = IssueFactory.create(user=developer,
                                        state=ISSUE_STATES.OPENED,
                                        due_date=monday + timedelta(days=4),
                                        total_time_spent=timedelta(
                                            hours=3).total_seconds(),
                                        time_estimate=timedelta(
                                            hours=10).total_seconds())

    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=4),
        user=developer,
        base=another_issue,
        time_spent=seconds(hours=3)
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=2, hours=5),
        user=developer,
        base=another_issue,
        time_spent=seconds(hours=2)
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1),
        user=developer,
        base=issue,
        time_spent=seconds(hours=4)
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1, hours=5),
        user=developer,
        base=issue,
        time_spent=-seconds(hours=3)
    )

    issue.time_estimate = seconds(hours=15)
    issue.total_time_spent = issue.time_spents.aggregate(
        spent=Sum("time_spent"),
    )["spent"]
    issue.state = ISSUE_STATES.OPENED
    issue.due_date = monday + timedelta(days=1)
    issue.save()

    another_issue.total_time_spent = another_issue.time_spents.aggregate(
        spent=Sum("time_spent"),
    )["spent"]
    another_issue.save()

    start = monday - timedelta(days=5)
    end = monday + timedelta(days=5)
    metrics = get_progress_metrics(team, start, end, "week")

    developer_metrics = next(
        item.metrics for item in metrics if item.user == developer)

    assert len(developer_metrics) == 2

    _check_metrics(developer_metrics,
                   {
                       monday: timedelta(hours=6)
                   }, {
                       monday: 2
                   }, {
                       monday: timedelta(days=1, hours=1)
                   }, {})


def _check_metrics(metrics,
                   spents: Dict[date, timedelta],
                   issues_counts: Dict[date, int],
                   time_estimates: Dict[date, timedelta],
                   efficiencies: Dict[date, float]):
    spents = _prepare_metrics(spents)
    time_estimates = _prepare_metrics(time_estimates)
    issues_counts = _prepare_metrics(issues_counts)
    efficiencies = _prepare_metrics(efficiencies)

    for metric in metrics:
        assert metric.end == metric.start + timedelta(weeks=1)

        _check_metric(metric, "time_spent", spents)
        _check_metric(metric, "time_estimate", time_estimates)

        start_dt = str(metric.start)
        if start_dt in efficiencies:
            assert efficiencies.get(start_dt) == metric.efficiency
        else:
            assert metric.efficiency == 0

        if start_dt in issues_counts:
            assert issues_counts.get(start_dt) == metric.issues_count
        else:
            assert metric.issues_count == 0


def _prepare_metrics(metrics):
    return {
        format_date(metric_date): time
        for metric_date, time in metrics.items()
    }


def _check_metric(metric, metric_name, values):
    dt = str(metric.start)

    if dt in values:
        assert getattr(metric, metric_name) == values.get(dt).total_seconds()
    else:
        assert getattr(metric, metric_name) == 0