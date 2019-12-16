def check_group(group, gl_group, parent=None):
    assert group.gl_id == gl_group.id
    assert group.gl_url == gl_group.web_url
    assert group.gl_avatar == gl_group.avatar_url
    assert group.title == gl_group.name
    assert group.full_title == gl_group.full_name

    if parent:
        assert group.parent == parent
    else:
        assert group.parent is None


def check_issue(issue, gl_issue):
    assert issue.gl_id == gl_issue.id
    assert issue.gl_iid == gl_issue.iid
    assert issue.gl_url == gl_issue.web_url
    assert issue.title == gl_issue.title
    assert issue.state == gl_issue.state.upper()
    assert issue.created_at is not None
    assert issue.updated_at is not None


def check_milestone(milestone, gl_milestone, owner):
    assert milestone.gl_id == gl_milestone.id
    assert milestone.gl_iid == gl_milestone.iid
    assert milestone.gl_url == gl_milestone.web_url
    assert milestone.title == gl_milestone.title
    assert milestone.description == gl_milestone.description
    assert milestone.start_date is not None
    assert milestone.due_date is not None
    assert milestone.created_at is not None
    assert milestone.updated_at is not None
    assert milestone.state == gl_milestone.state.upper()
    assert milestone.owner == owner


def check_merge_request(merge_request, gl_merge_request):
    assert merge_request.gl_id == gl_merge_request.id
    assert merge_request.gl_iid == gl_merge_request.iid
    assert merge_request.gl_url == gl_merge_request.web_url
    assert merge_request.title == gl_merge_request.title
    assert merge_request.state == gl_merge_request.state.upper()
    assert merge_request.created_at is not None
    assert merge_request.updated_at is not None


def check_project(project, gl_project, group=None):
    assert project.gl_id == gl_project.id
    assert project.gl_url == gl_project.web_url
    assert project.gl_avatar == gl_project.avatar_url
    assert project.title == gl_project.name
    assert project.full_title == gl_project.name_with_namespace

    if group:
        assert project.group == group
    else:
        assert project.group is None
