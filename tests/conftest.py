from tempfile import TemporaryDirectory

from gstui.gsclient import ThreadedCachedClient, CachedClient

import pytest


class MockedCachedClient(CachedClient):
    def __init__(self):
        pass


@pytest.fixture(scope="function")
def cache_path():
    with TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture(scope="function")
def cached_client(cache_path):
    ThreadedCachedClient.cache_path = cache_path
    return MockedCachedClient()
