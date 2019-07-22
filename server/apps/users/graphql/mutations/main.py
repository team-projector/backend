from .login import LoginMutation
from .gitlab.auth_complete import AuthCompleteMutation


class AuthMutations:
    login = LoginMutation.Field()
    auth_complete = AuthCompleteMutation.Field()
