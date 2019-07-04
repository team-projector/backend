from collections import namedtuple

from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.development.models import Team, TeamMember
from apps.development.rest.filters.serializers import TeamParamsSerializer
from tests.test_development.factories import TeamMemberFactory, TeamFactory
from tests.test_users.factories import UserFactory


class TeamParamsTests(TestCase):
    def test_bad_team(self):
        team = Team.objects.order_by('-id').first()
        team_id = (team.id if team else 0) + 1
        self.assertRaises(
            ValidationError,
            self.validate_serializer,
            param=team_id
        )

    def test_team_as_string(self):
        team_id = 'team'

        self.assertRaises(
            ValidationError,
            self.validate_serializer,
            param=team_id
        )

    def test_user_without_role(self):
        team = TeamFactory.create()
        user = UserFactory.create()

        team.members.add(user)

        context = {
            'request': namedtuple('Request', 'user')(user)
        }

        self.assertRaises(
            ValidationError,
            self.validate_serializer,
            param=team.id,
            context=context,
        )

    def test_user_developer_role(self):
        team = TeamFactory.create()
        user = UserFactory.create()

        context = {
            'request': namedtuple('Request', 'user')(user)
        }

        TeamMemberFactory.create(
            user=user,
            team=team,
            roles=TeamMember.roles.developer
        )

        self.assertRaises(
            ValidationError,
            self.validate_serializer,
            param=team.id,
            context=context,
        )

    def test_user_leader_role(self):
        team = TeamFactory.create()
        user = UserFactory.create()

        context = {
            'request': namedtuple('Request', 'user')(user)
        }

        TeamMemberFactory.create(
            user=user,
            team=team,
            roles=TeamMember.roles.leader
        )

        serializer = self.validate_serializer(
            param=team.id,
            context=context,
        )

        self.assertEqual(team.id, serializer.data['team'])

    def test_user_watcher_role(self):
        team = TeamFactory.create()
        user = UserFactory.create()

        context = {
            'request': namedtuple('Request', 'user')(user)
        }

        TeamMemberFactory.create(
            user=user,
            team=team,
            roles=TeamMember.roles.watcher
        )

        serializer = self.validate_serializer(
            param=team.id,
            context=context,
        )

        self.assertEqual(team.id, serializer.data['team'])

    def validate_serializer(self, param, **kwargs):
        data = {'team': param}
        serializer = TeamParamsSerializer(data=data, **kwargs)
        serializer.is_valid(raise_exception=True)

        return serializer
