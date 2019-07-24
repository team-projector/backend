from .gitlab.complete_gitlab_auth import CompleteGitlabAuthMutation
from .login import LoginMutation
from .logout import LogoutMutation


class AuthMutations:
    complete_gitlab_auth = CompleteGitlabAuthMutation.Field()
    login = LoginMutation.Field()
    logout = LogoutMutation.Field()
