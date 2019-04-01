"""Transmission daemon module."""

import logging
import subprocess
import threading
import time

from .parse_tms import parse_transmission_output


def exec_cmd(command, wait_after=None):
    """
    Execute specified command.

    If command fails or returns non zero code exception will be thrown.
    """
    logging.debug('Executing command: %s', command)
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    proc.wait()

    if proc.returncode:
        cmd = ' '.join(command)
        error = subprocess.CalledProcessError(
            returncode=proc.returncode, cmd=cmd,
            output=proc.stdout.read().decode('utf-8'))

        logging.error('Error executing command "%s"', cmd)
        logging.debug('Command "%s" output: [%s]', cmd, error.output, stack_info=True, exc_info=error)
        raise error

    if wait_after:
        time.sleep(wait_after)

    return proc.stdout.read().decode('utf-8')


class TransmissionDaemon:
    """Transmission daemon monitor thread."""

    def __init__(self):
        """Initialize the daemon class."""
        self._done = True
        self._listeners = []
        self._data = None
        self._started_daemon = False

    def _update(self):
        try:
            while not self._done:
                logging.debug('Updating transmission data')
                output = exec_cmd(['transmission-remote', '--torrent', 'all', '--info', '--files'])
                logging.debug('Fetched data: %s', output)

                self._data = parse_transmission_output(output)
                logging.debug('Parsed output: %s', self._data)

                self._notify(event='updated', transfers=[_extract_status_data(item['info']) for item in self._data])
                time.sleep(1)

        except subprocess.CalledProcessError:
            logging.error('Unable to talk to daemon')
            logging.debug('Error details', stack_info=True, exc_info=True)
            self._notify(event='daemon_stopped')

    def add_listener(self, listener):
        """Add object to receive events."""
        self._listeners.append(listener)

    def start(self):
        """Start monitoring the daemon thread."""
        try:
            try:
                logging.debug('Checking for running daemon')
                exec_cmd(['transmission-remote', '--list'])

            except FileNotFoundError:
                logging.error('Cannot find transmission-remote, make sure it\'s installed')
                logging.debug('Error details', stack_info=True, exc_info=True)
                return False

            except subprocess.CalledProcessError:
                logging.info('Starting Transmission daemon')
                exec_cmd(['transmission-daemon'], wait_after=3)
                self._started_daemon = True

            self._done = False
            threading.Thread(target=self._update).start()
            return True

        except FileNotFoundError:
            logging.error('Cannot find transmission-daemon, make sure it\'s installed')
            logging.debug('Error details', stack_info=True, exc_info=True)

        except subprocess.CalledProcessError:
            logging.error('Unable to start daemon')
            logging.debug('Error details', stack_info=True, exc_info=True)

        return False

    def stop(self):
        """Stop the daemon monitoring thread."""
        self._listeners = None

        try:
            if self._started_daemon:
                logging.info('Stopping Transmission daemon')
                exec_cmd(['transmission-remote', '--exit'], wait_after=2)

        except subprocess.CalledProcessError:
            logging.error('Unable to stop daemon')
            logging.debug('Error details', stack_info=True, exc_info=True)

        self._done = True

    def _notify(self, event, *args, **kwargs):
        for listener in self._listeners:
            event_method = getattr(listener, 'on_' + event, None)
            if callable(event_method):
                event_method(*args, **kwargs)


def _extract_status_data(info):
    data = info['transfer'].copy()
    data['id'] = info['name']['id']
    data['name'] = info['name']['name']
    return data
