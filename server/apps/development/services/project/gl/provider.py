# -*- coding: utf-8 -*-

from typing import Optional

from gitlab.v4 import objects as gl
from rest_framework import status

from apps.core.activity.decorators import gitlab_api_call
from apps.core.gitlab.provider import BaseGlProvider
from apps.development.models import Project


class ProjectGlProvider(BaseGlProvider):
    """Project gitlab provider."""

    @gitlab_api_call
    def get_gl_project(self, project: Project) -> Optional[gl.Project]:
        """Load project from gitlab."""
        try:
            return self.gl_client.projects.get(id=project.gl_id)
        except gl.GitlabGetError as error:
            if error.response_code == status.HTTP_404_NOT_FOUND:
                project.is_active = False
                project.save(update_fields=("is_active",))
            else:
                raise

        return None
