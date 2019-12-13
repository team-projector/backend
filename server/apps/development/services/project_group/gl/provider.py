# -*- coding: utf-8 -*-

from typing import Optional

from gitlab.v4 import objects as gl
from rest_framework import status

from apps.core.activity.decorators import gitlab_api_call
from apps.core.gitlab.provider import BaseGlProvider
from apps.development.models import ProjectGroup


class ProjectGroupGlProvider(BaseGlProvider):
    """Project groups gitlab provider."""

    @gitlab_api_call
    def get_gl_groups(self, **kwargs):
        """Load groups from gitlab."""
        return self.gl_client.groups.list(**kwargs)

    @gitlab_api_call
    def get_gl_group(self, group: ProjectGroup) -> Optional[gl.Group]:
        """Load group from gitlab."""
        try:
            return self.gl_client.groups.get(id=group.gl_id)
        except gl.GitlabGetError as error:
            if error.response_code == status.HTTP_404_NOT_FOUND:
                group.is_active = False
                group.save(update_fields=('is_active',))
            else:
                raise

        return None
