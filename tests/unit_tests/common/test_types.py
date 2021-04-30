from datetime import datetime

import pytest

from dsw_sdk.common.types import (
    AnyType,
    BoolType,
    DateTimeType,
    DictType,
    FloatType,
    IntegerType,
    ListType,
    MappingType, NoneType,
    NumericType,
    ObjectType,
    StringType,
    TupleType,
    UnionType,
)


class Foo:
    def __init__(self, **kwargs):
        self.attrs = kwargs
        for key, value in self.attrs.items():
            setattr(self, key, value)

    def __eq__(self, other):
        return self.attrs == other.attrs

    def to_json(self):
        return self.attrs


class FooBar(Foo):
    pass


COMPLEX_TYPE = UnionType(
    NumericType(),
    UnionType(
        TupleType(NumericType(), NumericType()),
        TupleType(StringType(), StringType()),
    ),
)
MAPPING_TYPE = MappingType(
    'type',
    {
        'a': ObjectType(Foo),
        'b': ObjectType(FooBar),
    },
)


@pytest.mark.parametrize('type_, value', [
    (AnyType(), None),
    (AnyType(), True),
    (AnyType(), 1234),
    (AnyType(), 'abcd'),
    (AnyType(), [(1,), {1, 2, 3}, ['a', 'b'], {None: None, 1: 1}]),
    (NoneType(), None),
    (BoolType(), False),
    (StringType(), 'some string'),
    (IntegerType(), 3),
    (FloatType(), 3.14),
    (NumericType(), 3),
    (NumericType(), 3.14),
    (UnionType(BoolType()), False),
    (UnionType(NoneType(), StringType(), FloatType()), None),
    (UnionType(NoneType(), StringType(), FloatType()), 'None'),
    (UnionType(NoneType(), StringType(), FloatType()), 0.0),
    (TupleType(), ()),
    (TupleType(BoolType()), (False,)),
    (TupleType(NoneType(), StringType(), FloatType()), (None, 'None', .0)),
    (TupleType(NoneType(), StringType(), FloatType()), [None, 'None', .0]),
    (ListType(), []),
    (ListType(IntegerType()), [1, 2, 3]),
    (ListType(DictType(StringType(), NoneType())), [{'a': None}, {'1': None}]),
    (DictType(StringType(), StringType()), {}),
    (DictType(IntegerType(), StringType()), {1: '1'}),
    (DictType(StringType(), BoolType()), {'n': True, 'None': True, '': True}),
    (UnionType(NoneType(), FloatType()), None),
    (UnionType(NoneType(), FloatType()), 3.14),
    (DateTimeType(), datetime.now()),
    (COMPLEX_TYPE, 3.14),
    (COMPLEX_TYPE, (3.14, 3.14)),
    (COMPLEX_TYPE, (3.14, 3)),
    (COMPLEX_TYPE, (3, 3.14)),
    (COMPLEX_TYPE, (3, 3)),
    (COMPLEX_TYPE, ('3.14', '3.14')),
    (ObjectType(Foo), Foo()),
    (MAPPING_TYPE, Foo(type='a', some_attr='123')),
    (MAPPING_TYPE, FooBar(type='b', some_attr='foo')),
])
def test_general_validation(type_, value):
    type_.validate(value)


@pytest.mark.parametrize('type_, value', [
    (NoneType(), False),
    (BoolType(), 'False'),
    (StringType(), 12345),
    (IntegerType(), 3.14),
    (IntegerType(), True),
    (FloatType(), 3),
    (NumericType(), '3.14'),
    (UnionType(BoolType()), ()),
    (UnionType(NoneType(), StringType(), FloatType()), False),
    (TupleType(BoolType()), ()),
    (TupleType(BoolType()), (False, False)),
    (TupleType(NoneType(), StringType(), FloatType()), ('None', None, .0)),
    (TupleType(NoneType(), StringType(), FloatType()), {None, 'None', .0}),
    (ListType(IntegerType()), (1, 2, 3)),
    (ListType(BoolType()), ['false', 'true']),
    (DictType(StringType(), NoneType()), {'key': 0}),
    (DictType(StringType(), StringType()), {'k1': 'v1', 'k2': '', 'k3': None}),
    (DateTimeType(), datetime.today().date()),
    (COMPLEX_TYPE, ('3.14', 3.14)),
    (COMPLEX_TYPE, ('3.14', 3)),
    (ObjectType(Foo), FooBar()),
    (MAPPING_TYPE, Foo(invalid_type_key='a', some_attr='123')),
    (MAPPING_TYPE, Foo(type='invalid_type_value', some_attr='123')),
])
def test_general_validation_fail(type_, value):
    with pytest.raises(ValueError):
        type_.validate(value)


@pytest.mark.parametrize('type_, value, result', [
    (AnyType(), 'none', 'none'),
    (AnyType(), None, None),
    (AnyType(), [1, '2', b'\x03'], [1, '2', b'\x03']),
    (NoneType(), 'none', None),
    (NoneType(), 'None', None),
    (NoneType(), 'NONE', None),
    (NoneType(), 'null', None),
    (NoneType(), 'Null', None),
    (NoneType(), 'NULL', None),
    (BoolType(), 'false', False),
    (BoolType(), 'False', False),
    (BoolType(), 'FALSE', False),
    (BoolType(), 'true', True),
    (BoolType(), 'True', True),
    (BoolType(), 'TRUE', True),
    (StringType(), 'abcd 1234', 'abcd 1234'),
    (StringType(), '', ''),
    (IntegerType(), '0', 0),
    (IntegerType(), '000000', 0),
    (IntegerType(), '0123', 123),
    (FloatType(), '0.0', 0),
    (FloatType(), '.0', 0),
    (FloatType(), '0', 0),
    (FloatType(), '000000', 0),
    (FloatType(), '0000.0', 0),
    (NumericType(), '3', 3),
    (NumericType(), '3.14', 3.14),
    (UnionType(NoneType(), FloatType()), 'None', None),
    (UnionType(NoneType(), FloatType()), 'null', None),
    (UnionType(NoneType(), FloatType()), '0.0', 0.0),
    (UnionType(NoneType(), FloatType()), '.0', 0.0),
    (UnionType(NoneType(), ListType(IntegerType())), (1, 2), [1, 2]),
    (UnionType(FloatType(), StringType()), '0.0', 0.0),
    (UnionType(StringType(), FloatType()), '0.0', '0.0'),
    (TupleType(), '', ()),
    (TupleType(), '()', ()),
    (TupleType(), '[]', ()),
    (TupleType(NoneType(), FloatType()), 'null,3.14', (None, 3.14)),
    (TupleType(NoneType(), FloatType()), '(None, 3.14)', (None, 3.14)),
    (TupleType(NoneType(), FloatType()), (None, '3.14'), (None, 3.14)),
    (TupleType(NoneType(), FloatType()), [None, '3.14'], (None, 3.14)),
    (ListType(), '', []),
    (ListType(), '[]', []),
    (ListType(IntegerType()), '[]', []),
    (ListType(IntegerType()), '[1, 2, 3]', [1, 2, 3]),
    (ListType(BoolType()), '[true, false]', [True, False]),
    (ListType(BoolType()), (True, 'false'), [True, False]),
    (
        DictType(StringType(), FloatType()),
        '{"a": 3.14, "b": 1.0}',
        {'a': 3.14, 'b': 1.0},
    ),
    (
        DictType(StringType(), FloatType()),
        "{'a': 3.14, 'b': 1.0}",
        {'a': 3.14, 'b': 1.0},
    ),
    (
        DictType(StringType(), FloatType()),
        '{"a": "3.14", "b": 1}',
        {'a': 3.14, 'b': 1.0},
    ),
    (
        DictType(StringType(), FloatType()),
        {"a": "3.14", "b": 1},
        {'a': 3.14, 'b': 1.0},
    ),
    (
        DictType(StringType(), DictType(StringType(), FloatType())),
        {"a": '{"3.14": 3.14}', "b": {"1": 1}},
        {"a": {"3.14": 3.14}, "b": {'1': 1}},
    ),
    (
        DateTimeType(),
        '2020-02-20T20:20:20Z',
        datetime(2020, 2, 20, 20, 20, 20),
    ),
    (
        DateTimeType(),
        '2021-04-05T22:25:08.124164524Z',
        datetime(2021, 4, 5, 22, 25, 8),
    ),
    (COMPLEX_TYPE, '3.14', 3.14),
    (COMPLEX_TYPE, '(3.14, .0123)', (3.14, .0123)),
    (COMPLEX_TYPE, '(3.14, 3)', (3.14, 3)),
    (COMPLEX_TYPE, '(def, .0123)', ('def', '.0123')),
    (
        ObjectType(Foo),
        {'a': 123, 'b': ['string']},
        Foo(a=123, b=['string']),
    ),
    (
        MAPPING_TYPE,
        {'type': 'a', 'other_attr': '123'},
        Foo(type='a', other_attr='123'),
    ),
    (
        MAPPING_TYPE,
        {'type': 'b', 'other_attr': '123'},
        FooBar(type='b', other_attr='123'),
    ),
])
def test_general_conversion(type_, value, result):
    assert type_.convert(value) == result


@pytest.mark.parametrize('type_, value', [
    (NoneType(), 'No'),
    (NoneType(), ''),
    (BoolType(), 'Falsch'),
    (BoolType(), 'No'),
    (BoolType(), 'yes'),
    (IntegerType(), '3.14'),
    (FloatType(), '3C'),
    (FloatType(), '3,14'),
    (NumericType(), '3..14'),
    (UnionType(NoneType(), FloatType()), 'true'),
    (UnionType(NoneType(), FloatType()), '1e'),
    (TupleType(IntegerType()), '()'),
    (TupleType(BoolType(), BoolType()), 'false'),
    (TupleType(BoolType(), BoolType()), 'false, None'),
    (TupleType(NoneType(), FloatType()), '  [  NONE  ,  3 . 1 4  ]  '),
    (TupleType(NoneType(), FloatType()), 123),
    (TupleType(NoneType(), FloatType()), True),
    (ListType(NoneType()), '()'),
    (ListType(BoolType()), '(false, false, false)'),
    (ListType(BoolType()), 42),
    (ListType(BoolType()), False),
    (DictType(StringType(), StringType()), '{invalid: json}'),
    (DictType(StringType(), StringType()), ['1', '2']),
    (DictType(StringType(), StringType()), [('key', 'value'), ('1', 2)]),
    (
        DictType(StringType(), TupleType(StringType(), StringType())),
        '{"k": "string"}',
    ),
    (
        DictType(StringType(), TupleType(StringType(), StringType())),
        '{"k": "()"}',
    ),
    (
        DictType(StringType(), TupleType(StringType(), StringType())),
        '{"k": "(a, b, c)"}',
    ),
    (DateTimeType(), '2020-02-20T'),
    (DateTimeType(), '2020-02-20 00:00:00'),
    (MAPPING_TYPE, {'invalid_key_for_type': 'a'}),
    (MAPPING_TYPE, {'type': 'invalid_value_for_type'}),
])
def test_general_conversion_fail(type_, value):
    with pytest.raises(ValueError):
        type_.convert(value)


@pytest.mark.parametrize('type_, expected', [
    (AnyType(), 'Any'),
    (NoneType(), 'NoneType'),
    (BoolType(), 'bool'),
    (StringType(), 'str'),
    (IntegerType(), 'int'),
    (FloatType(), 'float'),
    (UnionType(StringType(), IntegerType()), 'Union[str, int]'),
    (TupleType(BoolType(), BoolType()), 'Tuple[bool, bool]'),
    (ListType(TupleType(AnyType(), AnyType())), 'List[Tuple[Any, Any]]'),
    (DictType(StringType(), FloatType()), 'Dict[str, float]'),
    (DateTimeType(), 'datetime'),
    (NumericType(), 'Union[int, float]'),
    (
        COMPLEX_TYPE,
        'Union[int, float, Tuple[Union[int, float], '
        'Union[int, float]], Tuple[str, str]]',
    ),
    (ObjectType(Foo), 'Foo')
])
def test_type_to_str(type_, expected):
    assert str(type_) == expected


@pytest.mark.parametrize('type_, value, expected', [
    (AnyType(), [{'k': 'v'}, ('a',), {1, 2}], [{'k': 'v'}, ('a',), {1, 2}]),
    (NoneType(), None, None),
    (BoolType(), True, True),
    (StringType(), 'asdf', 'asdf'),
    (IntegerType(), 123, 123),
    (FloatType(), .1, .1),
    (
        UnionType(NoneType(), DictType(StringType(), BoolType()), FloatType()),
        3.14,
        3.14
    ),
    (TupleType(FloatType(), StringType()), (.1, 'abc'), [.1, 'abc']),
    (ListType(FloatType()), [.1, 2], [.1, 2]),
    (DictType(StringType(), BoolType()), {'a': True}, {'a': True}),
    (ObjectType(Foo), Foo(a=123, b='foo'), {'a': 123, 'b': 'foo'}),
    (MAPPING_TYPE, Foo(type='a', foo='1'), {'type': 'a', 'foo': '1'}),
])
def test_type_to_json(type_, value, expected):
    assert type_.to_json(value) == expected


@pytest.mark.parametrize('type_, value, expected', [
    (AnyType(), 123, '123'),
    (NoneType(), None, 'None'),
    (BoolType(), False, 'False'),
    (StringType(), 'foo', '"foo"'),
    (IntegerType(), 123, '123'),
    (FloatType(), 123.321, '123.321'),
    (UnionType(IntegerType(), FloatType(), BoolType()), 123.321, '123.321'),
    (UnionType(IntegerType(), FloatType(), BoolType()), 123, '123'),
    (UnionType(IntegerType(), FloatType(), BoolType()), True, 'True'),
    (TupleType(IntegerType(), BoolType()), (1, True), '(1, True)'),
    (TupleType(ObjectType(Foo)), (), '()'),
    (TupleType(ObjectType(Foo)), (Foo(), Foo()), '(...) (2 items)'),
    (ListType(NoneType()), [None, None], '[None, None]'),
    (ListType(ObjectType(Foo)), [], '[]'),
    (ListType(ObjectType(Foo)), [Foo()], '[...] (1 items)'),
    (DictType(StringType(), NoneType()), {'foo': None}, "{'foo': None}"),
    (DictType(StringType(), ObjectType(Foo)), {}, '{}'),
    (
        DictType(StringType(), ObjectType(Foo)),
        {'foo': Foo()},
        '{...} (1 items)',
    ),
    (ObjectType(Foo), Foo(foo=123), '<Foo ...>'),
    (MAPPING_TYPE, FooBar(foo=True, type='b'), '<FooBar ...>'),
])
def test_value_repr(type_, value, expected):
    assert type_.value_repr(value) == expected
