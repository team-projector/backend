from apps.development.graphql.types.project import ProjectType
from tests.test_development.factories import ProjectFactory
from tests.test_development.factories_gitlab import AttrDict


def test_project(user, client):
    client.user = user
    info = AttrDict({'context': client})

    project = ProjectFactory.create()

    assert ProjectType().get_node(info, project.id) == project
