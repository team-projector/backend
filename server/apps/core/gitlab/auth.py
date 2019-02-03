from django.http import JsonResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from social_core.backends.gitlab import GitLabOAuth2
from social_core.utils import handle_http_errors

from apps.users.rest.serializers import TokenSerializer
from apps.users.utils.token import create_user_token


class CustomGitLabOAuth2(GitLabOAuth2):
    @handle_http_errors
    def auth_complete(self, *args, **kwargs):
        user = super().auth_complete(*args, **kwargs)

        if not user:
            return Response(
                {'errors': {'token': 'Invalid token'}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = create_user_token(user)

        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        return JsonResponse(TokenSerializer(token).data)
