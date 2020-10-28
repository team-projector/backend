from apps.development.graphql.queries import (
    gitlab,
    issues,
    merge_requests,
    milestones,
    projects,
    teams,
    tickets,
    project_groups,
)


class DevelopmentQueries(  # noqa: WPS215
    issues.IssuesQueries,
    tickets.TicketsQueries,
    merge_requests.MergeRequestQueries,
    milestones.MilestonesQueries,
    projects.ProjectsQueries,
    teams.TeamsQueries,
    gitlab.GitlabQueries,
    project_groups.ProjectGroupsQueries,
):
    """Class represents list of all queries."""
