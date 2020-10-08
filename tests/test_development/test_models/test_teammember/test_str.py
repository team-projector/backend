from tests.test_development.factories import TeamFactory, TeamMemberFactory


def test_str(user):
    """
    Test str.

    :param user:
    """
    team = TeamFactory.create(title="team_title_test")
    member = TeamMemberFactory.create(user=user, team=team)

    assert str(member) == "team_title_test: {0}".format(user)
