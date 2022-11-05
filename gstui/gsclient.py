import os
from pathlib import Path
from shutil import rmtree
from threading import Thread
from typing import List

from diskcache import Cache
from google.cloud import storage
from tqdm.std import tqdm


class GsClient(storage.Client):
    def download(self, *_):
        pass


def get_cache_path() -> str:
    """Get cache path in different OS's"""
    if os.name == "nt":
        path = os.getenv("LOCALAPPDATA")
        if path is None:
            path = os.getenv("APPDATA")
        if path is None:
            print("Cannot find cache path")
            exit(1)
            return
        path = Path(path) / "gstui" / "cache"
    else:
        path = Path.home() / ".cache" / "gstui"
    return str(path)


class ThreadedCachedClient:
    """
    Cached client. Spawns a thread with the google client.
    In case something is not cached, it will join the thread and block.
    """

    init_thread: Thread
    thread_pool: List[Thread]
    cache_path: str = get_cache_path()

    def spawn(self, cls, *args, **kwargs):
        # spawn init in thread
        self.init_thread = Thread(
            target=cls.__init__, args=(self, *args), kwargs=kwargs
        )
        self.init_thread.start()
        self.thread_pool = []

    def clear_cache(self):
        """Clean cache"""
        print("Cleaning cache database...")
        rmtree(Path(self.cache_path).expanduser(), ignore_errors=True)

    def _thread_pool_cleanup(self):
        """Cleanup thread pool"""
        for thread in self.thread_pool:
            if not thread.is_alive():
                self.thread_pool.remove(thread)

    def close(self):
        """Stop all threads"""
        self._thread_pool_cleanup()
        print("Stopping all threads...")
        if self.init_thread.is_alive():
            self.init_thread.join()
        for thread in self.thread_pool:
            thread.join()

    @classmethod
    def diskcache(cls, func):
        """Decorator to cache function results to disk"""

        def wrapper(self, *args, **kwargs):
            if not isinstance(self, ThreadedCachedClient):
                raise TypeError(
                    "Decorator only works with ThreadedCachedClient")
            cache = Cache(cls.cache_path)
            key = func.__name__ + ":" + str(args) + str(kwargs)
            result = cache.get(key)
            if result is None:
                # Ensure init thread is finished otherwise join it
                if self.init_thread.is_alive():
                    self.init_thread.join()
                result = func(self, *args, **kwargs)
                cache.set(key, result)
            elif not self.init_thread.is_alive():
                new_thread = Thread(target=func, args=(
                    self, *args), kwargs=kwargs)
                self.thread_pool.append(new_thread)
                new_thread.start()
                self._thread_pool_cleanup()

            return result

        return wrapper


class CachedClient(GsClient, ThreadedCachedClient):
    """Google cloud storage ThreadedCachedClient"""

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.spawn(GsClient, *args, **kwargs)

    def close(self):
        super().close()
        ThreadedCachedClient.close(self)

    @ThreadedCachedClient.diskcache
    def list_buckets(self, *args, **kwargs) -> List[str]:
        return [
            bucket.name for bucket in super().list_buckets(*args, **kwargs)
        ]

    @ThreadedCachedClient.diskcache
    def list_blobs(self, *args, **kwargs) -> List[str]:
        return [blob.name for blob in super().list_blobs(*args, **kwargs)]

    def cache_all(self):
        """Cache all tree structure"""
        print("Caching all tree structure. This might take a while...")
        buckets = self.list_buckets()
        for bucket in tqdm(buckets):
            self.list_blobs(bucket)

    # TODO part of this should be responsability of the UI instead
    def download(self, blob: storage.Blob, destination_file_name: str):
        if blob.size is not None:
            print(f"Downloading {blob.size/1024/1024:.2f} MB")
        with open(destination_file_name, "wb") as f:
            with tqdm.wrapattr(f, "write", total=blob.size) as file_obj:
                self.download_blob_to_file(blob, file_obj)
        print(f"Downloaded {Path(destination_file_name).name}")
