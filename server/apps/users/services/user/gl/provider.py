# -*- coding: utf-8 -*-

from apps.core.gitlab.provider import BaseGlProvider


class UserGlProvider(BaseGlProvider):
    """User gitlab provider."""

    def get_gl_user(
        self,
        gl_user_id: int,
    ):
        """Get user from gitlab."""
        return self.gl_client.users.get(gl_user_id)
