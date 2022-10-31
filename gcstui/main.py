# List buckets in GCS

from google.cloud import storage
from diskcache import Cache
from pathlib import Path
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
    def list_buckets(self, *args, **kwargs) -> [str]:
        return [bucket.name for bucket in super().list_buckets(*args, **kwargs)]

    @diskcache
    def list_blobs(self, *args, **kwargs) -> [str]:
        return [blob.name for blob in super().list_blobs(*args, **kwargs)]


storage_client = CachedClient()


def list_buckets():
    buckets = storage_client.list_buckets()
    fzf = FzfPrompt()
    bucket_name = fzf.prompt(buckets)[0]
    if bucket_name:
        blobs = storage_client.list_blobs(bucket_name)
        blob_name = fzf.prompt(blobs)[0]
        if blob_name:
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            destination_file_name = Path(blob_name).name
            with open(destination_file_name, 'wb') as f:
                with tqdm.wrapattr(f, "write", total=blob.size) as file_obj:
                    storage_client.download_blob_to_file(blob, file_obj)
            print(f"Downloaded {blob_name}")
            return

    print("No blob selected")


if __name__ == '__main__':
    list_buckets()
