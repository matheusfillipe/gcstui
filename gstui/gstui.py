# List buckets in GCS

from pathlib import Path
from typing import List

from diskcache import Cache
from google.cloud import storage
from pyfzf.pyfzf import FzfPrompt
from tqdm.std import tqdm

CACHE_PATH = Path.home() / ".cache" / "pytermgui"


# Cache decorator
def diskcache(func):
    def wrapper(self, *args, **kwargs):
        cache = Cache(str(CACHE_PATH))
        key = func.__name__ + ":" + str(args) + str(kwargs)
        result = cache.get(key)
        if result is None:
            result = func(self, *args, **kwargs)
            cache.set(key, result)
        else:
            ...
            # print("Found cached")
        return result

    return wrapper


class CachedClient(storage.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @diskcache
    def list_buckets(self, *args, **kwargs) -> List[str]:
        return [
            bucket.name for bucket in super().list_buckets(*args, **kwargs)
        ]

    @diskcache
    def list_blobs(self, *args, **kwargs) -> List[str]:
        return [blob.name for blob in super().list_blobs(*args, **kwargs)]


storage_client = CachedClient()


def mainloop():
    fzf = FzfPrompt()
    buckets = storage_client.list_buckets()
    bucket_name = None
    while True:
        try:
            if bucket_name is None:
                bucket_name = fzf.prompt(buckets)[0]
            else:
                blobs = storage_client.list_blobs(bucket_name)
                blob_name = fzf.prompt(blobs)[0]
                if blob_name:
                    bucket = storage_client.bucket(bucket_name)
                    blob = bucket.blob(blob_name)
                    destination_file_name = Path(blob_name).name
                    if blob.size is not None:
                        print(f"Downloading {blob.size/1024/1024:.2f} MB")
                    with open(destination_file_name, "wb") as f:
                        with tqdm.wrapattr(f, "write", total=blob.size) \
                                as file_obj:
                            storage_client.download_blob_to_file(
                                blob, file_obj)
                    print(f"Downloaded {blob_name}")
        except KeyboardInterrupt:
            return
