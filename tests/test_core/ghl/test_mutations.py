from pytest import raises

from apps.core.graphql.mutations import BaseMutation, ArgumentsValidationMixin


def test_base_mutation():
    with raises(NotImplementedError):
        BaseMutation().do_mutate(root=None, info=None)


def test_arguments_validation():
    with raises(NotImplementedError):
        ArgumentsValidationMixin().perform_mutate(info=None, data=None)
