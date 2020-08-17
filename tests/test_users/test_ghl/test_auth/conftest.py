# -*- coding: utf-8 -*-

import pytest


@pytest.fixture(scope="session")
def login_mutation(ghl_mutations):
    """
    Login mutation.

    :param ghl_mutations:
    """
    return ghl_mutations.fields["login"].resolver


@pytest.fixture(scope="session")
def logout_mutation(ghl_mutations):
    """
    Logout mutation.

    :param ghl_mutations:
    """
    return ghl_mutations.fields["logout"].resolver


@pytest.fixture(scope="session")
def complete_gl_auth_mutation(ghl_mutations):
    """
    Complete gl auth mutation.

    :param ghl_mutations:
    """
    return ghl_mutations.fields["completeGitlabAuth"].resolver
