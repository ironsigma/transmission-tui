"""Transfer list components."""

import curses
import logging
import math

from .colors import Colors

SECONDS_PER_DAY = 60 * 60 * 24
SECONDS_PER_HOUR = 60 * 60
SECONDS_PER_MINUTE = 60


class TransferList:
    """Transfer list component."""

    def __init__(self, stdscr):
        """Initialize the component."""
        self._stdscr = stdscr
        self._count = 0
        self._selected = None
        self._transfers = []

        self._stdscr.erase()
        self._stdscr.addstr(1, 2, 'Waiting for connection to daemon')

    def select_previous(self):
        """Select the previous item on the list."""
        if self._count == 0:
            return

        if self._selected is None:
            self._selected = self._transfers[-1]['id']
            self.on_updated(self._transfers)
            return

        found = False
        for item in reversed(self._transfers):
            if found:
                self._selected = item['id']
                break

            if self._selected == item['id']:
                found = True
        else:
            self._selected = None

        self.on_updated(self._transfers)

    def select_next(self):
        """Select the next item on the list."""
        if self._count == 0:
            return

        if self._selected is None:
            self._selected = self._transfers[0]['id']
            self.on_updated(self._transfers)
            return

        found = False
        for item in self._transfers:
            if found:
                self._selected = item['id']
                break

            if self._selected == item['id']:
                found = True
        else:
            self._selected = None

        self.on_updated(self._transfers)

    def on_updated(self, transfers):
        """Receive transmission daemon updates."""
        self._stdscr.erase()

        (_height, width) = self._stdscr.getmaxyx()
        self._count = len(transfers)
        self._transfers = transfers

        if transfers:
            for (index, item) in enumerate(transfers):
                self._progress_bar(0, index * 4, width, item)
        else:
            self._selected = None
            self._stdscr.addstr(1, 2, 'No active transfers')

        self._stdscr.refresh()

    def on_daemon_stopped(self):
        """Update the screen when daemon connection is lost."""
        self._stdscr.erase()
        self._stdscr.addstr(1, 2, 'Lost connection to daemon')
        self._stdscr.refresh()

    def _progress_bar(self, x, y, width, item):
        percent = float(item['percent done'][0:-1])
        if math.isnan(percent):
            fill = 0
            percent = 'N/A'
        else:
            fill = int(width * (percent / 100.0))
            percent = f'{percent}%'

        have = _extract_up_to(item['have'], ' (')

        if item['state'] == 'Finished':
            eta = 'Done'
        elif item['state'] == 'Idle':
            eta = 'N/A'
        else:
            eta = _abbr_eta(item['eta'])

        logging.debug('ETA %s to %s', item['eta'], eta)

        self._stdscr.addstr(
            y, x,
            '  Done      Have  ETA                 '
            'Up        Down  Ratio  Status       Name', curses.A_BOLD)

        self._stdscr.addstr(
            y + 1, x,
            f'{percent:>6} {have:>9}  {eta:<10} {item["upload speed"]:>11} '
            f'{item["download speed"]:>11} {item["ratio"]:>6}  {item["state"]:<11}  '
            f'{item["name"][0:72]:<30}')

        if fill:
            self._stdscr.addstr(y + 2, x, " " * fill, Colors.color(Colors.PROGRESS_FILLED))

        if fill < width:
            self._stdscr.addstr(y + 2, x + fill, " " * (width - fill), Colors.color(Colors.PROGRESS_EMPTY))

        if self._selected == item['id']:
            self._stdscr.chgat(y, x, width, Colors.color(Colors.ITEM_SELECTED_HEADER) | curses.A_BOLD)
            self._stdscr.chgat(y + 1, x, width, Colors.color(Colors.ITEM_SELECTED))


def _abbr_eta(time):
    index = time.index('(')
    seconds = int(time[index + 1:time.index(' ', index)])

    if seconds == 0:
        return 'done'

    if seconds < SECONDS_PER_MINUTE:
        return f'{seconds} secs'

    days = int(seconds / SECONDS_PER_DAY)
    if days > 2:
        return f'{days} days'

    remainder = seconds % SECONDS_PER_DAY
    hours = int(remainder / SECONDS_PER_HOUR)

    remainder = remainder % SECONDS_PER_HOUR
    minutes = int(remainder / SECONDS_PER_MINUTE)

    if days:
        return f'{days}d {hours:02}:{minutes:02}'

    if hours:
        return f'{hours}:{minutes:02} hrs'

    seconds = remainder % SECONDS_PER_MINUTE
    return f'{minutes}.{seconds:02} mins'


def _extract_up_to(string, boundary):
    try:
        return string[0:string.index(boundary)]
    except ValueError:
        return string
