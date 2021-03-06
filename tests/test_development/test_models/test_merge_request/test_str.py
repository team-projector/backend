from tests.test_development.factories import MergeRequestFactory


def test_str(db):
    """
    Test str.

    :param db:
    """
    merge_request = MergeRequestFactory.create(
        title="merge_request_title_test",
    )

    assert str(merge_request) == "merge_request_title_test"
