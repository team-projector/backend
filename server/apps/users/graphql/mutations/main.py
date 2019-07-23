from .login import LoginMutation
from .gitlab.complete_gitlab_auth import CompleteGitlabAuthMutation


class AuthMutations:
    login = LoginMutation.Field()
    complete_gitlab_auth = CompleteGitlabAuthMutation.Field()
