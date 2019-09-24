# -*- coding: utf-8 -*-

from gitlab.v4.objects import (
    Project as GlProject,
    ProjectIssue as GlProjectIssue,
)

from apps.development.models import Issue, MergeRequest, Project
from ..merge_requests import load_project_merge_request


def load_merge_requests(issue: Issue,
                        project: Project,
                        gl_issue: GlProjectIssue,
                        gl_project: GlProject) -> None:
    def get_merge_request(gl_id: int, gl_iid: int) -> MergeRequest:
        merge_request = MergeRequest.objects.filter(gl_id=gl_id).first()

        if not merge_request:
            gl_merge_request = gl_project.mergerequests.get(gl_iid)

            merge_request = load_project_merge_request(
                project, gl_project, gl_merge_request,
            )

        return merge_request

    issue.merge_requests.set((
        get_merge_request(item['id'], item['iid'])
        for item in gl_issue.closed_by()
    ))
