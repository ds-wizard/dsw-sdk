import re


def to_camel_case(string: str) -> str:
    if string.find('_') == -1:
        return string
    return re.sub(
        r'(.)(_)(.)',
        lambda m: f'{m.group(1)}{m.group(3).upper()}',
        string.lower().strip('_')
    )


def to_snake_case(string: str) -> str:
    string = re.sub(r'(.)([A-Z][a-z])', r'\1_\2', string)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', string).lower()


def truncate_long_string(string: str, max_len: int) -> str:
    index = string.find('\n')
    index = index if index != -1 else max_len
    return f'"{string[:index]}..." (truncated)'
