from threading import Thread
from tempfile import TemporaryDirectory

from gstui.gsclient import ThreadedCachedClient, CachedClient
from pathlib import Path

import pytest


class MockedCachedClient(CachedClient):
    def __init__(self):
        self.init_thread = Thread()
        self.thread_pool = []


@pytest.fixture(scope="function")
def cache_path():
    with TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture(scope="function")
def cached_client(cache_path):
    ThreadedCachedClient.cache_path = cache_path
    return MockedCachedClient()


@pytest.fixture(scope="function")
def temp_file():
    with TemporaryDirectory() as tmpdir:
        yield Path(tmpdir) / Path("file.temp")
