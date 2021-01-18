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
    mock_create_project_hook,
    mock_delete_project_hook,
)
from .users import register_user
from .notes import mock_create_note_issue_endpoint
