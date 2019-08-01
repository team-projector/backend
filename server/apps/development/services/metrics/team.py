from apps.development.models import Issue, MergeRequest, Team, TeamMember
from apps.development.models.issue import STATE_OPENED
from apps.development.services.problems.issue import annotate_issues_problems, \
    filter_issues_problems


class WorkItemMetrics:
    count: int = 0
    opened_count: int = 0


class IssuesMetrics(WorkItemMetrics):
    pass


class MergeRequestMetrics(WorkItemMetrics):
    pass


class TeamMetrics:
    problems_count: int = 0
    issues: IssuesMetrics
    merge_requests: MergeRequestMetrics


class TeamMetricsProvider:
    def __init__(self,
                 issues: Issue,
                 merge_requests: MergeRequest):
        self.issues = issues
        self.merge_requests = merge_requests

    def execute(self) -> TeamMetrics:
        metrics = TeamMetrics()

        metrics.issues = IssuesMetrics()
        metrics.issues.count = self.issues.count()
        metrics.issues.opened_count = self._get_opened_workitems_count(
            self.issues
        )

        metrics.merge_requests = MergeRequestMetrics()
        metrics.merge_requests.count = self.merge_requests.count()
        metrics.merge_requests.opened_count = self._get_opened_workitems_count(
            self.merge_requests
        )

        problems_issues = annotate_issues_problems(self.issues)
        problems_issues = filter_issues_problems(problems_issues)
        metrics.problems_count = problems_issues.count()

        return metrics

    @staticmethod
    def _get_opened_workitems_count(items) -> int:
        return items.filter(state=STATE_OPENED).count()


def get_team_metrics(team: Team) -> TeamMetrics:
    users = TeamMember.objects.get_no_watchers(team)

    issues = Issue.objects.filter(user__in=users)
    merge_requests = MergeRequest.objects.filter(user__in=users)

    provider = TeamMetricsProvider(
        issues,
        merge_requests
    )

    return provider.execute()
