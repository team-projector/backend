from urllib.parse import parse_qs

from django.db import close_old_connections

from apps.users.models import Token


class TokenAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        user = self.get_user_from_scope(scope)

        close_old_connections()

        return self.inner(dict(scope, user=user))

    def get_user_from_scope(self, scope):
        try:
            query_string = scope['query_string']
            if isinstance(query_string, bytes):
                query_string = query_string.decode('utf-8')

            token_key = parse_qs(query_string)['token'][0]
            token = Token.objects.get(key=token_key)
            return token.user
        except (Token.DoesNotExist, KeyError):
            return None
