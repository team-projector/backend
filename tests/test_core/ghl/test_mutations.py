from pytest import raises

from apps.core.graphql.mutations import ArgumentsValidationMixin, BaseMutation


def test_base_mutation():
    with raises(NotImplementedError):
        BaseMutation().do_mutate(root=None, info=None)


def test_arguments_validation():
    with raises(NotImplementedError):
        ArgumentsValidationMixin().perform_mutate(info=None, cleaned_data=None)
