"""
Utility methods and helpers.
"""

import re


def to_camel_case(string: str) -> str:
    """
    Converts a string from snake_case to camelCase.

    :param string: string in snake_case notation

    :return: `string` converted to camelCase
    """
    if string.find('_') == -1:
        return string
    return re.sub(
        r'(.)(_)(.)',
        lambda m: f'{m.group(1)}{m.group(3).upper()}',
        string.lower().strip('_')
    )


def to_snake_case(string: str) -> str:
    """
    Converts a string from camelCase to snake_case.

    :param string: string in camelCase notation

    :return: `string` converted to snake_case
    """
    string = re.sub(r'(.)([A-Z][a-z])', r'\1_\2', string)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', string).lower()


def truncate_long_string(string: str, max_len: int) -> str:
    """
    Truncates the given text from the first newline character. If no
    newline is present in the ``string``, truncate text to ``max_len``
    characters.
    If the text is shorter than ``max_len``, does nothing.

    :param string: text to truncate
    :param max_len: maximal length of the truncated string

    :return: truncated string, enquoted in double quotes, with the
             ``(truncated)`` string appended at the end
    """
    if len(string) <= max_len:
        return string
    index = string.find('\n')
    index = index if (index != -1 and index <= max_len) else max_len
    return f'"{string[:index]}..." (truncated)'
