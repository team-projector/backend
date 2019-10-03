# -*- coding: utf-8 -*-

from .gitlab.complete_gitlab_auth import CompleteGitlabAuthMutation
from .gitlab.login import LoginGitlabMutation
from .login import LoginMutation
from .logout import LogoutMutation


class AuthMutations:
    """
    A class representing list of available fields for authorization.
    """
    complete_gitlab_auth = CompleteGitlabAuthMutation.Field()
    login_gitlab = LoginGitlabMutation.Field()
    login = LoginMutation.Field()
    logout = LogoutMutation.Field()
