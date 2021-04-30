import pytest

from dsw_sdk.common.utils import (
    to_camel_case,
    to_snake_case,
    truncate_long_string,
)


@pytest.mark.parametrize('value, expected', [
    ('', ''),
    ('snake_case', 'snakeCase'),
    ('BIG_CASE', 'bigCase'),
    ('Capital_Snake_Case', 'capitalSnakeCase'),
    ('123_snake_with_4numbers', '123SnakeWith4numbers'),
    ('$0me_$pec1al_#characters', '$0me$pec1al#characters'),
    ('_private_string', 'privateString'),
    ('non_shadowing_string_', 'nonShadowingString'),
    ('__name_mangling', 'nameMangling'),
    ('1234', '1234'),
    ('camelCase', 'camelCase'),
])
def test_to_camel_case(value, expected):
    assert to_camel_case(value) == expected


@pytest.mark.parametrize('value, expected', [
    ('', ''),
    ('camelCase', 'camel_case'),
    ('PascalCase', 'pascal_case'),
    ('BIGCASE', 'bigcase'),
    ('BIG_CASE', 'big_case'),
    ('camel123WithNumbers', 'camel123_with_numbers'),
    ('$pecial#Characters', '$pecial#_characters'),
    ('1234', '1234'),
    ('snake_case', 'snake_case'),
])
def test_to_snake_case(value, expected):
    assert to_snake_case(value) == expected


def test_truncate_long_string():
    assert truncate_long_string('long text', 3) == '"lon..." (truncated)'
