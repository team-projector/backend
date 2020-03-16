# -*- coding: utf-8 -*-

from .merge_requests import (
    register_merge_request,
    register_merge_request_time_stats,
    register_merge_request_labels,
    register_merge_request_notes,
    mock_merge_request_endpoints,
)
from .projects import (
    register_project,
    register_project_issues,
    register_project_labels,
    register_project_merge_requests,
    register_create_project_hook,
    register_delete_project_hook,
    mock_project_endpoints,
)
from .issues import (
    register_issue,
    register_issue_labels,
    register_issue_notes,
    register_issue_participants,
    register_issue_closed_by,
    register_issue_time_stats,
    mock_issue_endpoints,
)
from .users import register_user
from .groups import (
    register_group_milestones,
    register_group,
    register_groups,
    mock_group_endpoints,
)
from .group_milestones import (
    register_group_milestone,
    mock_group_milestone_endpoints,
)
from .project_milestones import (
    register_project_milestone,
    mock_project_milestone_endpoints,
)
