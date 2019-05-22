from datetime import timedelta

from django.test import TestCase

from apps.development.services.metrics.milestones import get_milestone_metrics
from tests.test_development.factories import IssueFactory, ProjectMilestoneFactory
from tests.test_payroll.factories import IssueSpentTimeFactory
from tests.test_users.factories import UserFactory


class MilestoneMetricsTests(TestCase):
    def setUp(self):
        super().setUp()

        self.milestone = ProjectMilestoneFactory.create(budget=10000)
        self.user = UserFactory.create(hour_rate=1000)

    def test_payrolls(self):
        issue_1 = IssueFactory.create(user=self.user, milestone=self.milestone)
        issue_2 = IssueFactory.create(user=self.user, milestone=self.milestone)
        issue_3 = IssueFactory.create(user=self.user)

        IssueSpentTimeFactory.create(user=self.user, base=issue_1, time_spent=timedelta(hours=1).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, base=issue_1, time_spent=timedelta(hours=2).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, base=issue_2, time_spent=-timedelta(hours=1).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, base=issue_3, time_spent=timedelta(hours=3).total_seconds())

        metrics = get_milestone_metrics(self.milestone)

        self.assertEqual(metrics.budget, self.milestone.budget)
        self.assertEqual(metrics.payroll, 2000)
        self.assertEqual(metrics.profit, 8000)

    def test_payrolls_no_spents(self):
        IssueFactory.create(user=self.user, milestone=self.milestone)
        IssueFactory.create(user=self.user, milestone=self.milestone)
        IssueFactory.create(user=self.user)

        metrics = get_milestone_metrics(self.milestone)

        self.assertEqual(metrics.budget, self.milestone.budget)
        self.assertEqual(metrics.payroll, 0)
        self.assertEqual(metrics.profit, self.milestone.budget)

    def test_payrolls_no_issues(self):
        metrics = get_milestone_metrics(self.milestone)

        self.assertEqual(metrics.budget, self.milestone.budget)
        self.assertEqual(metrics.payroll, 0)
        self.assertEqual(metrics.profit, self.milestone.budget)

    def test_payrolls_no_budget(self):
        self.milestone.budget = 0
        self.milestone.save()

        metrics = get_milestone_metrics(self.milestone)

        self.assertEqual(metrics.budget, self.milestone.budget)
        self.assertEqual(metrics.payroll, 0)
        self.assertEqual(metrics.profit, self.milestone.budget)
