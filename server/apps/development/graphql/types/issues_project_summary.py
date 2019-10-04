# -*- coding: utf-8 -*-

import graphene

from .project import ProjectType
from .project_issues_summary import ProjectIssuesSummary


class IssuesProjectSummary(graphene.ObjectType):
    """
    Issues project summary.
    """
    project = graphene.Field(ProjectType)
    issues = graphene.Field(ProjectIssuesSummary)

    def resolve_project(self, info, **kwargs):
        """
        Get project.
        """
        # we need this to apply IssuesProjectSummary specific behaviour
        self.project.parent_type = self
        return self.project
