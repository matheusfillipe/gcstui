import time
from dataclasses import dataclass
from pathlib import Path
from time import sleep
from unittest.mock import patch

from gstui.gsclient import CachedClient, ThreadedCachedClient, get_cache_path

CACHE_KEYS = [(1,), ("no", "cache"), (1, 2, "args")]
CACHE_MAP = {
    CACHE_KEYS[0]: ["a", "b", "c"],
    CACHE_KEYS[1]: ["d", "e", "f"],
    CACHE_KEYS[2]: ["g", "h", "i", 3],
}


class MockSlowClass:
    def __init__(self, sleep_time):
        sleep(sleep_time)

    def slow_method(self, sleep_time):
        sleep(sleep_time)


class MockClient(MockSlowClass, ThreadedCachedClient):
    def __init__(self, *args):
        self.spawn(MockSlowClass, *args)

    @ThreadedCachedClient.diskcache
    def slow_method(self, sleep_time):
        return super().slow_method(sleep_time)

    @ThreadedCachedClient.diskcache
    def cache1(self, a1):
        sleep(0.1)
        return CACHE_MAP[(a1,)]

    @ThreadedCachedClient.diskcache
    def cache2(self, a1, a2):
        sleep(0.1)
        return CACHE_MAP[(a1, a2)]

    @ThreadedCachedClient.diskcache
    def cache3(self, a1, a2, a3):
        sleep(0.1)
        return CACHE_MAP[(a1, a2, a3)]


def test_threading_blocking(cache_path: str):
    ThreadedCachedClient.cache_path = cache_path
    start = time.time()
    client = MockClient(1)
    client.slow_method(1)
    total = time.time() - start
    assert total >= 2.0


def test_threading_non_blocking(cache_path: str):
    ThreadedCachedClient.cache_path = cache_path
    start = time.time()
    MockClient(1)
    total = time.time() - start
    assert total < 1


def assert_caching(method, *args):
    start = time.time()
    client = MockClient(0.05)
    method = getattr(client, method)
    assert method(*args) == CACHE_MAP[args]
    total = time.time() - start
    assert total >= 0.1
    start = time.time()
    assert method(*args) == CACHE_MAP[args]
    total = time.time() - start
    assert total < 0.1


def test_caching(cache_path: str):
    ThreadedCachedClient.cache_path = cache_path
    assert_caching("cache1", *CACHE_KEYS[0])
    assert_caching("cache2", *CACHE_KEYS[1])
    assert_caching("cache3", *CACHE_KEYS[2])


@dataclass
class MockBlob:
    name: str
    size: int = 1024


@patch("gstui.gsclient.super")
def test_cache_usage(mock_super, cached_client: CachedClient):
    mock_super().list_buckets.return_value = [
        MockBlob(name) for name in ["a", "b", "c"]
    ]
    mock_super().list_blobs.return_value = [
        MockBlob(name) for name in ["d", "e", "f"]]
    cached_client.cache_all()
    path = (Path(cached_client.cache_path) / "cache.db").expanduser()

    assert path.exists()
    assert path.stat().st_size > 0

    cached_client.clear_cache()
    assert not path.exists()
