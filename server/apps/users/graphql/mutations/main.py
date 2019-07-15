from .login import LoginMutation


class AuthMutations:
    login = LoginMutation.Field()
