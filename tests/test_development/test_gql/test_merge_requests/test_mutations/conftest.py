import pytest


@pytest.fixture(scope="session")
def sync_merge_request_mutation(ghl_mutations):
    """Sync merge request mutation."""
    return ghl_mutations.fields["syncMergeRequest"].resolver
