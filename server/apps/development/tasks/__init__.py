# -*- coding: utf-8 -*-

from .issues import (
    sync_issues_task,
    sync_project_issue_task,
    sync_project_issues_task,
    propagate_ticket_to_related_issues_task,
)
from .merge_requests import (
    sync_merge_requests_task,
    sync_project_merge_request_task,
    sync_project_merge_requests_task,
)
from .milestones import (
    sync_project_group_milestones_task,
    sync_project_milestones_task,
    sync_project_group_milestone_task,
    sync_groups_milestones_task,
    sync_project_milestone_task,
    sync_projects_milestones_task,
)
from .project_groups import sync_project_group_task
from .projects import sync_project_task
from .sync_all import sync_all_task
from .users import sync_user_task
