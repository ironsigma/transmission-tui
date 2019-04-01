"""Functions to parse Transmission output."""

import logging
import re


def reduce(function, iterable, initial):
    """
    Functional reduce function.

    Take an iterable and apply the specified function to each element.
    The result is fed into the next function call.
    """
    accumulator = initial
    for (index, item) in enumerate(iterable):
        accumulator = function(accumulator, item, index, iterable)
    return accumulator


def compose(*functions):
    """
    Create a function that will chain the specified functions.

    Example:

    >>> transform = compose(
    ...     str.strip,
    ...     str.lower
    ... )
    >>> transform(['    NUMBERS 123  '])
    'numbers 123'
    """
    return lambda args: reduce(
        lambda accumulator, function, _index, _functions: function(accumulator), functions, args)


def _read_data_from_file(filename):
    return open(filename).read()


def _split_transfer_items(data):
    boundary = 'NAME\n'
    return [(boundary + text) for text in data.split(boundary)][1:]


def _split_info_into_sections(info):
    return info.strip().split('\n\n')


def _section_to_keys(info):
    parse_info = compose(
        _text_to_value_lines,
        _lines_values_to_dict
    )

    sections = {}
    for section in info:
        index = section.find('\n')
        sections[section[0:index].lower()] = parse_info(section[index + 1:])

    return sections


def _text_to_value_lines(text):
    return [line.strip() for line in text.split('\n')]


def _lines_values_to_dict(lines):
    return {
        key.lower(): value.strip() for (key, value) in
        [line.split(':', 1) for line in lines]}


def _split_and_filter_files(text):
    return [
        line
        for line in text.strip().split('\n')
        if line.find('files):') == -1 and line.find('Done Priority') == -1]


def _convert_files_to_dictionary(lines):
    files = []
    for line in lines:
        match = re.search(r'(\d+):\s+([0-9]+%)\s+(\S+)\s+(\S+)\s+([0-9.]+ \S+)\s+(.*)$', line)
        files.append({
            'id': match.group(1),
            'done': match.group(2),
            'priority': match.group(3),
            'get': match.group(4),
            'size': match.group(5),
            'name': match.group(6)
        })
    return files


def _parse_info_and_files(item):
    parse_info = compose(
        _split_info_into_sections,
        _section_to_keys
    )

    parse_file_data = compose(
        _split_and_filter_files,
        _convert_files_to_dictionary
    )

    try:
        index = item.index('files):\n')
        index = item.rfind('\n', 0, index)
        return {'info': parse_info(item[0:index]), 'files': parse_file_data(item[index + 1:])}
    except ValueError:
        return {'info': parse_info(item), 'files': []}


def parse_transmission_output(output):
    """Parse Transmission daemon output."""
    if output.find('NAME\n') == -1:
        logging.debug('No items found in output: %s', output)
        return []

    parse = compose(
        _split_transfer_items,
        lambda items: [_parse_info_and_files(item) for item in items],
    )
    return parse(output)
