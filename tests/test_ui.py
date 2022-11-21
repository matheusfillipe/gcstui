import random
import string
from unittest.mock import Mock

from gstui.gsclient import CachedClient
from gstui.ui_base import FzfUI, UIBase, View
from pyfzf.pyfzf import FzfPrompt


def generage_random_view() -> View:
    return View(
        [random.choice(string.ascii_letters) for _ in range(10)],
        random.choice(string.ascii_letters),
        random.choice([True, False]),
    )


def assert_stack_ui(ui: UIBase):
    test_view = generage_random_view()
    ui.push(test_view)
    assert ui.pop() == test_view
    view_list = []
    for _ in range(3):
        test_view = generage_random_view()
        view_list.append(test_view)
        ui.push(test_view)
    for _ in range(3):
        assert ui.pop() == view_list.pop()


def test_base_ui():
    test_base_ui = UIBase()
    assert_stack_ui(test_base_ui)


def test_fzf_ui(cached_client: CachedClient):
    mock_blob_name = "test"
    fzf = FzfPrompt()
    fzf.prompt = Mock(return_value=[mock_blob_name])
    test_fzf_ui = FzfUI(fzf)
    assert_stack_ui(test_fzf_ui)

    cached_client.bucket = Mock(return_value=Mock())
    cached_client.list_buckets = Mock(return_value=[mock_blob_name, "other"])
    cached_client.list_blobs = Mock(return_value=[mock_blob_name])

    # Use side effect to raise KeyboardInterrupt
    cached_client.download = Mock(side_effect=KeyboardInterrupt)
    test_fzf_ui.mainloop(cached_client)

    # Check call_args of download
    blob, name = cached_client.download.call_args[0]
    assert blob.name, name == [mock_blob_name] * 2
