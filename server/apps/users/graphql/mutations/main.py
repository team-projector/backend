# -*- coding: utf-8 -*-

from apps.users.graphql.mutations.gitlab.complete_gitlab_auth import (
    CompleteGitlabAuthMutation,
)
from apps.users.graphql.mutations.gitlab.login import LoginGitlabMutation
from apps.users.graphql.mutations.login import LoginMutation
from apps.users.graphql.mutations.logout import LogoutMutation


class AuthMutations:
    """A class representing list of available fields for authorization."""

    complete_gitlab_auth = CompleteGitlabAuthMutation.Field()
    login_gitlab = LoginGitlabMutation.Field()
    login = LoginMutation.Field()
    logout = LogoutMutation.Field()
