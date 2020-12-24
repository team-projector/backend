from constance import config
from django.http import HttpResponseBadRequest
from django.utils import timezone
from social_core.backends.gitlab import GitLabOAuth2 as SocialGitLabOAuth2
from social_core.utils import handle_http_errors

from apps.core import injector
from apps.users.models import User
from apps.users.services.token import TokenService


class GitLabOAuth2Backend(SocialGitLabOAuth2):
    """
    GitLab OAuth authentication backend.

    After successful authentication, a token is created.
    Create application: https://gitlab.com/profile/applications
    """

    @handle_http_errors
    def auth_complete(self, *args, **kwargs):
        """
        Do GitLab OAuth and return token.

        User must be exist in DB.
        """
        user = super().auth_complete(*args, **kwargs)

        if not user:
            return HttpResponseBadRequest("Invalid token")

        token_service = injector.get(TokenService)
        token = token_service.create_user_token(user)

        user.last_login = timezone.now()
        user.save(update_fields=("last_login",))

        return token  # noqa: WPS331

    def get_redirect_uri(self, state=None):
        """Callback URL after approving access on Gitlab."""
        return self.setting("REDIRECT_URI")

    def authenticate(self, *args, **kwargs):
        """Return authenticated user."""
        response = kwargs.get("response")

        if response:
            return User.objects.filter(login=response["username"]).first()

    def set_data(self, **kwargs):
        """
        Set data.

        For example "state" and "code" values returned from Gitlab.
        """
        self.data = kwargs  # noqa: WPS110

    def get_key_and_secret(self):
        """Return tuple with Consumer Key and Consumer Secret."""
        return config.OAUTH_GITLAB_KEY, config.OAUTH_GITLAB_SECRET
