"""Curses color definitions."""

import curses


class Colors:
    """Colors used."""

    PROGRESS_EMPTY = 1
    PROGRESS_FILLED = 2
    ITEM_SELECTED = 3
    ITEM_SELECTED_HEADER = 4

    @staticmethod
    def color(c):
        """Return selected color."""
        return curses.color_pair(c)

    @classmethod
    def init_color_pairs(cls):
        """Initialize the color pairs."""
        curses.init_pair(cls.PROGRESS_EMPTY, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(cls.PROGRESS_FILLED, curses.COLOR_BLUE, curses.COLOR_WHITE)
        curses.init_pair(cls.ITEM_SELECTED_HEADER, curses.COLOR_WHITE, curses.COLOR_GREEN)
        curses.init_pair(cls.ITEM_SELECTED, curses.COLOR_BLACK, curses.COLOR_GREEN)
