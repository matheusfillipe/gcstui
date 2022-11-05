from abc import abstractmethod
from queue import LifoQueue
from typing import List, Optional
from dataclasses import dataclass

from pyfzf.pyfzf import FzfPrompt
from gstui.gsclient import GsClient

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
    def mainloop(self):
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

    def __init__(self):
        self.fzf = FzfPrompt()
        super().__init__()

    def list_view(self, view: View) -> List[str]:
        items = view.items
        title = view.title
        multi = view.multi
        return self.fzf.prompt(items, f"{'--multi ' * multi}--prompt={title}")

    def mainloop(self, storage_client: GsClient):
        buckets = storage_client.list_buckets()
        bucket_name = None
        while True:
            try:
                if bucket_name is None:
                    view = View(buckets, "Bucket: ")
                    bucket_name = uistack.push(view)[0]
                else:
                    blobs = storage_client.list_blobs(bucket_name)
                    blob_name = uistack.push(View(blobs, "blob", True))
                    if blob_name:
                        bucket = storage_client.bucket(bucket_name)
                        blob = bucket.blob(blob_name)
                        download(blob, blob_name)
            except KeyboardInterrupt:
                return
