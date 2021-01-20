from apps.users.graphql.mutations import auth, users


class UsersMutations:
    """A class represents list of available mutations."""

    complete_gitlab_auth = auth.CompleteGitlabAuthMutation.Field()
    login_gitlab = auth.LoginGitlabMutation.Field()
    login = auth.LoginMutation.Field()
    logout = auth.LogoutMutation.Field()
    update_me = users.UpdateMeMutation.Field()
