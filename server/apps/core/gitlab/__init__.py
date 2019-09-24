# -*- coding: utf-8 -*-

import gitlab
from django.conf import settings


def get_gitlab_client(token: str = None) -> gitlab.Gitlab:
    gl = gitlab.Gitlab(settings.GITLAB_HOST, token or settings.GITLAB_TOKEN)
    gl.auth()

    return gl
