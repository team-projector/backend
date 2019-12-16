from pytest import raises

from apps.core.graphql.mutations import BaseMutation


def test_base_mutation():
    with raises(NotImplementedError):
        BaseMutation().do_mutate(root=None, info=None)
