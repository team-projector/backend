# -*- coding: utf-8 -*-

import pytest

from tests.helpers.asset_provider import AssetsProvider


@pytest.fixture()
def assets(request):
    provider = AssetsProvider(request.fspath.dirname)
    yield provider
    provider.close()