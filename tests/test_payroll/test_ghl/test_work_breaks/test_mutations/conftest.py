import pytest


@pytest.fixture(scope="session")
def update_work_break_mutation(ghl_mutations):
    """Update work break mutation."""
    return ghl_mutations.fields["updateWorkBreak"].resolver


@pytest.fixture(scope="session")
def approve_work_break_mutation(ghl_mutations):
    """Approve work break mutation."""
    return ghl_mutations.fields["approveWorkBreak"].resolver


@pytest.fixture(scope="session")
def decline_work_break_mutation(ghl_mutations):
    """Approve work break mutation."""
    return ghl_mutations.fields["declineWorkBreak"].resolver
