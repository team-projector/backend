from django.http import HttpResponseBadRequest, JsonResponse
from django.utils import timezone
from social_core.backends.gitlab import GitLabOAuth2 as SocialGitLabOAuth2
from social_core.utils import handle_http_errors

from apps.users.models import User
from apps.users.rest.serializers import TokenSerializer
from apps.users.services.token import create_user_token


class GitLabOAuth2Backend(SocialGitLabOAuth2):
    @handle_http_errors
    def auth_complete(self, *args, **kwargs):
        user = super().auth_complete(*args, **kwargs)

        if not user:
            return HttpResponseBadRequest('Invalid token')

        token = create_user_token(user)

        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        return JsonResponse(TokenSerializer(token).data)

    def get_redirect_uri(self, state=None):
        return self.setting('REDIRECT_URI')

    def authenticate(self, *args, **kwargs):
        if 'response' in kwargs:
            return User.objects.filter(
                login=kwargs['response']['username']
            ).first()

    def set_data(self, **kwargs):
        self.data = kwargs
