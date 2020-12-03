from apps.core.activity.decorators import gitlab_api_call
from apps.core.gitlab.provider import BaseGlProvider


class UserGlProvider(BaseGlProvider):
    """User gitlab provider."""

    @gitlab_api_call
    def get_gl_user(self, gl_user_id: int):
        """Get user from gitlab."""
        return self.gl_client.users.get(gl_user_id)
