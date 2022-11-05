from gstui.ui_base import FzfUI
from gstui.gsclient import CachedClient
from click import command, option, Choice


@command()
@option('--interface', '-i', default='fzf', type=Choice(['fzf']))
def main():
    storage_client = CachedClient()
    FzfUI().mainloop(storage_client)
