from abc import abstractmethod
from pathlib import Path
from dataclasses import dataclass
from queue import LifoQueue
from typing import List, Optional

from pyfzf.pyfzf import FzfPrompt

from gstui.gsclient import CachedClient


@dataclass
class View:
    items: List[str]
    title: Optional[str]
    multi: bool = False


class UIBase:
    """Base class for stack of list view UIs"""

    def __init__(self):
        self.view_stack = LifoQueue()

    @abstractmethod
    def list_view(self, view: View) -> List[str]:
        """List view of the items"""
        pass

    @abstractmethod
    def mainloop(self, client: CachedClient):
        """Main loop"""
        pass

    def push(self, view: View):
        """Adds a list view to the stack"""
        values = self.list_view(view)
        self.view_stack.put(view)
        return values

    def pop(self) -> View:
        """Pops a list view from the stack"""
        return self.view_stack.get()


class FzfUI(UIBase):
    """Default UI"""

    def __init__(self, fzf: FzfPrompt = FzfPrompt()):
        self.fzf = fzf
        super().__init__()

    def list_view(self, view: View) -> List[str]:
        items = view.items
        title = view.title
        multi = view.multi
        return self.fzf.prompt(items,
                               f"{'--multi ' * multi}--prompt='{title}'")

    def mainloop(self, storage_client: CachedClient):
        buckets = storage_client.list_buckets()
        bucket_name = None
        while True:
            try:
                if bucket_name is None:
                    view = View(buckets, "Bucket: ")
                    bucket_name = self.push(view)
                    if not bucket_name:
                        break
                    bucket_name = bucket_name[0]
                else:
                    blobs = storage_client.list_blobs(bucket_name)
                    blob_names = self.push(View(blobs, "Blob: ", True))
                    if not blob_names:
                        bucket_name = None
                        self.pop()
                        self.pop()
                        continue
                    self.pop()
                    for blob_name in blob_names:
                        bucket = storage_client.bucket(bucket_name)
                        blob = bucket.blob(blob_name)
                        storage_client.download(blob, Path(blob_name).name)
            except KeyboardInterrupt:
                return
