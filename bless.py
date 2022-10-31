#!/usr/bin/env python

from dataclasses import dataclass
from typing import Callable, List, Optional

from blessed import Terminal


@dataclass
class MenuOption:
    title: str
    action: Optional[Callable]


class ListMenu:
    def __init__(self, opts: List[MenuOption]):
        """
        Represents a menu

        :param opts List[MenuOption]: A list of options
        """
        self.opts = opts
        self.menu = [o.title for o in opts]

    def display_screen(self, selection):
        term = self.term = Terminal()
        print(term.clear())

        for (idx, m) in enumerate(self.menu):
            if idx == selection:
                print("{t.bold_red_reverse}{title}".format(t=term, title=m))
            else:
                print("{t.normal}{title}".format(t=term, title=m))

    def run_selection(self, opt: MenuOption):
        if opt.action:
            opt.action()

    def show(self):
        term = Terminal()
        with term.fullscreen():
            selection = 0
            self.display_screen(selection)
            selection_inprogress = True
            with term.cbreak():
                while selection_inprogress:
                    key = term.inkey()
                    if key.name in ["KEY_TAB", "KEY_DOWN"] or str(key).lower() == "j":
                        selection += 1
                    if key.name in ["KEY_BTAB", "KEY_UP"] or str(key).lower() == "k":
                        selection -= 1
                    if key.name == "KEY_ENTER":
                        selection_inprogress = False

                    selection = selection % len(self.menu)

                    self.display_screen(selection)

        self.run_selection(selection)


if __name__ == "__main__":
    menu = ListMenu([MenuOption(t, action=None) for t in ["login to system", "create account", "disconnect", "check it out"]])
    menu.show()
