# -*- coding: utf-8 -*-

from apps.development.graphql.queries import (
    gitlab,
    issues,
    merge_requests,
    milestones,
    projects,
    teams,
    tickets,
)


class DevelopmentQueries(  # noqa: WPS215
    issues.IssuesQueries,
    tickets.TicketsQueries,
    merge_requests.MergeRequestQueries,
    milestones.MilestonesQueries,
    projects.ProjectsQueries,
    teams.TeamsQueries,
    gitlab.GitlabQueries,
):
    """Class representing list of all queries."""
