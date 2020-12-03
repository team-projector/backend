from http import HTTPStatus


class _ProjectMocker:
    def __init__(self, mocker, project):
        """Initialize."""
        self._mocker = mocker
        self._project = project

    def mock_project(self, status_code: int = HTTPStatus.OK):
        """
        Register project.

        :param status_code:
        :type status_code: int, defaults to HTTPStatus.OK
        """
        self._mocker.register_get(
            "/projects/{0}".format(self._project["id"]),
            self._project,
            status_code=status_code,
        )

    def mock_hooks(self, hooks):
        """
        Register project hooks.

        :param hooks:
        """
        self._mocker.register_get(
            "/projects/{0}/hooks".format(self._project["id"]),
            hooks,
        )

    def mock_labels(self, labels):
        """
        Register project labels.

        :param labels:
        """
        self._mocker.register_get(
            "/projects/{0}/labels".format(self._project["id"]),
            labels,
        )

    def mock_issues(self, issues):
        """
        Register project issues.

        :param issues:
        """
        self._mocker.register_get(
            "/projects/{0}/issues".format(self._project["id"]),
            issues,
        )

    def mock_milestones(self, milestones):
        """
        Register project milestones.

        :param milestones:
        """
        self._mocker.register_get(
            "/projects/{0}/milestones".format(self._project["id"]),
            milestones,
        )
        for milestone in milestones:
            self._mocker.register_get(
                "/projects/{0}/milestones/{1}".format(
                    self._project["id"],
                    milestone["id"],
                ),
                milestone,
            )

    def mock_merge_requests(self, merge_requests):
        """
        Register project merge requests.

        :param merge_requests:
        """
        self._mocker.register_get(
            "/projects/{0}/merge_requests".format(self._project["id"]),
            merge_requests,
        )


def mock_create_project_hook(mocker, project, response):
    """
    Register create project hook.

    :param mocker:
    :param project:
    :param response:
    """
    mocker.register_post("/projects/{0}/hooks".format(project["id"]), response)


def mock_delete_project_hook(mocker, project, response=None):
    """
    Register delete project hook.

    :param mocker:
    :param project:
    :param response:
    """
    mocker.register_delete(
        "/projects/{0}/hooks".format(project["id"]),
        response,
    )


def mock_project_endpoints(
    mocker,
    project,
    status_code: int = HTTPStatus.OK,
    **kwargs,
):
    """
    Mock project endpoints.

    :param status_code:
    :param mocker:
    :param project:
    """
    project_mocker = _ProjectMocker(mocker, project)
    project_mocker.mock_project(status_code)
    project_mocker.mock_issues(kwargs.get("issues", []))
    project_mocker.mock_labels(kwargs.get("labels", []))
    project_mocker.mock_milestones(kwargs.get("milestones", []))
    project_mocker.mock_hooks(kwargs.get("hooks", []))
    project_mocker.mock_merge_requests(kwargs.get("merge_requests", []))
