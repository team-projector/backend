import gitlab
from django.conf import settings


def get_gitlab_client() -> gitlab.Gitlab:
    gl = gitlab.Gitlab(settings.GITLAB_HOST, settings.GITLAB_TOKEN)
    gl.auth()

    return gl
