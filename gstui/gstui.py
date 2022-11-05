import pkg_resources
from click import Choice, command, option

from gstui.gsclient import CachedClient
from gstui.ui_base import FzfUI


@command()
@option(
    "--interface", "-i", default="fzf", type=Choice(["fzf"]),
    help="UI interface to use"
)
@option("--clean", "-c", is_flag=True, help="Clean cache")
@option("--cache-path", "-p", default="~/.cache/gstui", help="Cache directory")
@option("--cache-all", "-a", is_flag=True, help="Cache all tree structure")
@option("--version", "-v", is_flag=True, help="Display version")
def main(interface, clean, cache_path, cache_all, version):
    storage_client = CachedClient()
    storage_client.cache_path = cache_path
    if version:
        print(pkg_resources.get_distribution("gstui").version)
        return
    if clean:
        storage_client.clear_cache()
        return
    if cache_all:
        storage_client.cache_all()
        return
    if interface == "fzf":
        ui = FzfUI()
        ui.mainloop(storage_client)
    storage_client.close()
