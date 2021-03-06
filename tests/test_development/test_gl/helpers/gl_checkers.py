KEY_ID = "id"
KEY_WEB_URL = "web_url"


def check_group(group, gl_group, parent=None):  # noqa: WPS218
    """
    Check group.

    :param group:
    :param gl_group:
    :param parent:
    """
    assert group.gl_id == gl_group[KEY_ID]
    assert group.gl_url == gl_group[KEY_WEB_URL]
    assert group.gl_avatar == gl_group["avatar_url"]
    assert group.title == gl_group["name"]
    assert group.full_title == gl_group["full_name"]
    assert group.parent == parent


def check_issue(issue, gl_issue):  # noqa: WPS218
    """
    Check issue.

    :param issue:
    :param gl_issue:
    """
    assert issue.gl_id == gl_issue[KEY_ID]
    assert issue.gl_iid == gl_issue["iid"]
    assert issue.gl_url == gl_issue[KEY_WEB_URL]
    assert issue.title == gl_issue["title"]
    assert issue.state == gl_issue["state"].upper()
    assert issue.created_at is not None
    assert issue.updated_at is not None


def check_milestone(milestone, gl_milestone, owner):  # noqa: WPS218
    """
    Check milestone.

    :param milestone:
    :param gl_milestone:
    :param owner:
    """
    assert milestone.gl_id == gl_milestone[KEY_ID]
    assert milestone.gl_iid == gl_milestone["iid"]
    assert milestone.gl_url == gl_milestone[KEY_WEB_URL]
    assert milestone.title == gl_milestone["title"]
    assert milestone.description == gl_milestone["description"]
    assert milestone.state == gl_milestone["state"].upper()
    assert milestone.start_date is not None
    assert milestone.due_date is not None
    assert milestone.created_at is not None
    assert milestone.updated_at is not None
    assert milestone.owner == owner


def check_merge_request(merge_request, gl_merge_request):  # noqa: WPS218
    """
    Check merge request.

    :param merge_request:
    :param gl_merge_request:
    """
    assert merge_request.gl_id == gl_merge_request[KEY_ID]
    assert merge_request.gl_iid == gl_merge_request["iid"]
    assert merge_request.gl_url == gl_merge_request[KEY_WEB_URL]
    assert merge_request.title == gl_merge_request["title"]
    assert merge_request.state == gl_merge_request["state"].upper()
    assert merge_request.created_at is not None
    assert merge_request.updated_at is not None


def check_project(project, gl_project, group=None):  # noqa: WPS218
    """
    Check project.

    :param project:
    :param gl_project:
    :param group:
    """
    assert project.gl_id == gl_project[KEY_ID]
    assert project.gl_url == gl_project[KEY_WEB_URL]
    assert project.gl_avatar == gl_project["avatar_url"]
    assert project.title == gl_project["name"]
    assert project.full_title == gl_project["name_with_namespace"]
    assert project.group == group


def check_user(user, gl_user):
    """
    Check user.

    :param user:
    :param gl_user:
    """
    assert user.login == gl_user["username"]
    assert user.email == gl_user["public_email"]
    assert user.name == gl_user["name"]
    assert user.gl_avatar == gl_user["avatar_url"]
    assert user.gl_url == gl_user[KEY_WEB_URL]
