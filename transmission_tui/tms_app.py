"""The Transmission text based user interface application module."""

import curses
import logging
import time

from .colors import Colors
from .daemon import TransmissionDaemon
from .logging_config import config_logging
from .transfer_list import TransferList


class TransmissionApp():
    """The main thread listening to user input."""

    def __init__(self):
        """Initialize the app."""
        config_logging()
        logging.debug("Starting Transmission TUI...")
        self._transmission = None
        self._stdscr = None

    def start(self):
        """Start the transmission daemon monitoring thread."""
        self._transmission = TransmissionDaemon()
        if not self._transmission.start():
            return

        curses.wrapper(self.start_ui)

    def start_ui(self, stdscr):
        """Start the user input thread."""
        self._stdscr = stdscr
        self._init_curses()

        transfer_list = TransferList(stdscr)
        self._transmission.add_listener(transfer_list)
        self._transmission.add_listener(self)

        logging.debug('Listening for user input')
        while True:
            char = stdscr.getch()
            if char == ord('q'):
                logging.debug('Requested quit')
                self._transmission.stop()
                break

            elif char == ord('k'):
                logging.debug('Selection up')
                transfer_list.select_previous()

            elif char == ord('j'):
                logging.debug('Selection down')
                transfer_list.select_next()

            time.sleep(.25)

    def _init_curses(self):
        Colors.init_color_pairs()
        curses.curs_set(0)
        self._stdscr.clear()
        self._stdscr.refresh()


if __name__ == '__main__':
    TransmissionApp().start()
