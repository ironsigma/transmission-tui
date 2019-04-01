"""Logging configuration module."""

import logging
import sys


def config_logging():
    """Configure logging."""
    (console_log_level, log_filename) = parse_command_line()

    log_handlers = []

    if log_filename:
        file_formatter = logging.Formatter(
            fmt='%(asctime)s %(levelname)7s [%(threadName)s] '
                '%(module)s.%(funcName)s: %(message)s')

        file_handler = logging.FileHandler(log_filename, mode='a')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        log_handlers.append(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_log_level)
    log_handlers.append(console_handler)

    logging.basicConfig(
        level=logging.NOTSET,
        format='%(levelname)s: %(message)s',
        handlers=log_handlers)


def parse_command_line():
    """Parse logging configuration from command line."""
    logging_levels = {
        'CRIT': logging.CRITICAL,
        'CRITICAL': logging.CRITICAL,
        'ERROR': logging.ERROR,
        'WARN': logging.WARNING,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
        'TRACE': logging.DEBUG,
        'NONE': None
    }

    log_filename = None
    console_log_level = logging.ERROR

    for arg in sys.argv:
        if arg.find('--log-file=') != -1:
            log_filename = arg[11:]

        elif arg.find('--log-level=') != -1:
            try:
                console_log_level = logging_levels[arg[12:].upper()]
            except KeyError:
                print(f'Invalid logging level: {arg[12:]}')

    return (console_log_level, log_filename)
