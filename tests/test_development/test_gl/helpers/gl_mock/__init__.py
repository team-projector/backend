# -*- coding: utf-8 -*-

from .group_milestones import (
    mock_group_milestone_endpoints,
    register_group_milestone,
)
from .groups import (
    mock_group_endpoints,
    register_group,
    register_group_milestones,
    register_groups,
)
from .issues import (
    mock_issue_endpoints,
    register_issue,
    register_issue_closed_by,
    register_issue_labels,
    register_issue_notes,
    register_issue_participants,
    register_issue_time_stats,
)
from .merge_requests import (
    mock_merge_request_endpoints,
    register_merge_request,
    register_merge_request_labels,
    register_merge_request_notes,
    register_merge_request_time_stats,
)
from .project_milestones import (
    mock_project_milestone_endpoints,
    register_project_milestone,
)
from .projects import (
    mock_project_endpoints,
    register_create_project_hook,
    register_delete_project_hook,
    register_project,
    register_project_issues,
    register_project_labels,
    register_project_merge_requests,
)
from .users import register_user
