from apps.development.models import Issue, Team, TeamMember
from apps.development.models.issue import STATE_OPENED
from apps.development.services.problems.issue import annotate_issues_problems, \
    filter_issues_problems


class TeamMetrics:
    issues_count: int = 0
    problems_count: int = 0
    issues_opened_count: int = 0
    # remains: float = 0
    # efficiency: float = 0


def get_team_metrics(team: Team) -> TeamMetrics:
    users = TeamMember.objects.get_no_watchers(team)
    issues = Issue.objects.filter(user__in=users)

    metrics = TeamMetrics()
    metrics.issues_count = issues.count()

    problems_issues = annotate_issues_problems(issues)
    problems_issues = filter_issues_problems(problems_issues)
    metrics.problems_count = problems_issues.count()

    metrics.issues_opened_count = issues.filter(
        state=STATE_OPENED
    ).count()

    return metrics
