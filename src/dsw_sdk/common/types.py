"""
Module containing all the data types used with :class:`~common.Attribute`
classes.
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Sized,
    Type as TypingType,
    TypeVar,
    Union,
)

from dsw_sdk.common.utils import to_camel_case


T = TypeVar('T')  # pylint: disable=C0103


class Type:
    """
    The most general type, parent for all specific types.
    """
    _type: TypingType

    def __repr__(self):
        return str(self)

    def __str__(self):
        # This is how the type will be displayed to the users in
        # error messages. Usually we want to display corresponding
        # builtin type or type from the typing module.
        return str(self._type.__name__)

    def _from_string(self, value: str) -> Any:
        """
        Used for converting from string value.

        :param value: string value to be converted to ``self._type`` type

        :return: possibly converted value
        """
        return value

    def validate(self, value: Any):
        """
        Validates if ``value`` is of correct data type.

        :param value: value to be validated

        :raises: :exc:`ValueError` if validation fails
        """
        # Not performing instance check (`isinstance`), but comparing types
        # directly because we want subclasses to fail this check, e.g.
        # `isinstance(True, int)` would pass but `type(True) == int` not
        if not type(value) == self._type:  # pylint: disable=C0123
            raise ValueError

    def convert(self, value: Any) -> Any:
        """
        Tries to convert ``value`` to ``self._type`` data type.

        :param value: value to be converted

        :return: possibly converted value, but it might also
                 be just the original value
        """
        if isinstance(value, str):
            return self._from_string(value)
        return value

    def to_json(self, value: Any) -> Any:
        """
        Converts the ``value`` to JSON.

        Be aware, that the result is not a string, but is instead
        represented with built-in Python types.

        :param value: value to be converted

        :return: JSON representation of the ``value``
        """
        return value

    def value_repr(self, value: Any) -> str:
        """
        Returns the string representation of the ``value`` for
        the ``self._type`` data type.

        :param value: value to be represented as a string

        :return: string representing ``value`` for this particular data type
        """
        return str(value)


class AnyType(Type):
    def __str__(self):
        return 'Any'

    def validate(self, value: Any):
        pass

    def convert(self, value: Any) -> Any:
        return value


class NoneType(Type):
    _type = type(None)

    def _from_string(self, value: str) -> Optional[str]:
        if value.lower() in ('none', 'null'):
            return None
        return value


class BoolType(Type):
    _type = bool

    def _from_string(self, value: str) -> Union[bool, str]:
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        return value


class StringType(Type):
    _type = str

    def convert(self, value: Any) -> str:
        return str(value)

    def value_repr(self, value: str) -> str:
        return f'"{value}"'


class IntegerType(Type):
    _type = int

    def convert(self, value: Any) -> int:
        try:
            # Converting to string first in order
            # not to convert bool or float values
            return int(str(value))
        except ValueError:
            return value


class FloatType(Type):
    _type = float

    def convert(self, value: Any) -> float:
        try:
            # Converting to string first in order
            # not to convert bool values
            return float(str(value))
        except ValueError:
            return value


class UnionType(Type):
    def __init__(self, *of_types: Type):
        self._of_types = of_types

    def __str__(self):
        types = []
        for type_ in self._of_types:
            if isinstance(type_, UnionType):
                types.extend(str(t) for t in type_._of_types)
            else:
                types.append(str(type_))
        return f'Union[{", ".join(types)}]'

    def _iter_over_types(self, value, callback):
        for type_ in self._of_types:
            try:
                return callback(type_, value)
            except ValueError:
                pass
        raise ValueError

    def validate(self, value: Any):
        self._iter_over_types(value, lambda type_, val: type_.validate(val))

    def convert(self, value: Any) -> Any:
        def callback(type_, val):
            converted = type_.convert(val)
            type_.validate(converted)
            return converted

        try:
            return self._iter_over_types(value, callback)
        except ValueError:
            return value

    def to_json(self, value: Any) -> Any:
        def callback(type_, val):
            type_.validate(val)
            return type_.to_json(val)

        return self._iter_over_types(value, callback)

    def value_repr(self, value: Any) -> str:
        def callback(type_, val):
            type_.validate(val)
            return type_.value_repr(val)

        return self._iter_over_types(value, callback)


class TupleType(Type):
    _type = tuple

    def __init__(self, *of_types: Type):
        self._of_types = of_types

    def __str__(self):
        types_str = ', '.join([str(type) for type in self._of_types])
        return f'Tuple[{types_str}]'

    def validate(self, value: Any):
        if not isinstance(value, (list, tuple)):
            raise ValueError
        if len(value) != len(self._of_types):
            raise ValueError
        for val, type_ in zip(value, self._of_types):
            type_.validate(val)

    def _from_string(self, value: str) -> Union[tuple, List[str]]:
        values = value.replace(' ', '').lstrip('(').rstrip(')').split(',')
        if values == ['']:
            return ()
        return values

    def convert(self, value: Any) -> tuple:
        converted = super().convert(value)
        if isinstance(converted, Sized) and isinstance(converted, Iterable):
            if len(self._of_types) != len(converted):
                return value
            res = []
            for val, type_ in zip(converted, self._of_types):
                converted_val = type_.convert(val)
                try:
                    # Checking that each item of the
                    # tuple is converted correctly
                    type_.validate(converted_val)
                except ValueError:
                    # Otherwise we must return the original value
                    return value
                res.append(converted_val)
            return tuple(res)
        return value

    def to_json(self, value: tuple) -> list:
        return [t.to_json(v) for v, t in zip(value, self._of_types)]

    def value_repr(self, value: tuple) -> str:
        if (
            any(isinstance(type_, (ObjectType, MappingType))
                for type_ in self._of_types)
            and value
        ):
            return f'(...) ({len(value)} items)'
        return str(value)


class ListType(Type):
    _type = list

    def __init__(self, of_type: Type = AnyType()):
        self._of_type = of_type

    def __str__(self):
        return f'List[{str(self._of_type)}]'

    def validate(self, value: Any):
        super().validate(value)
        for val in value:
            self._of_type.validate(val)

    def _from_string(self, value: str) -> list:
        values = value.replace(' ', '').lstrip('[').rstrip(']').split(',')
        if values == ['']:
            return []
        return values

    def convert(self, value: Any) -> list:
        converted_value = super().convert(value)
        if isinstance(converted_value, Iterable):
            res = []
            for val in converted_value:
                converted_val = self._of_type.convert(val)
                try:
                    self._of_type.validate(converted_val)
                except ValueError:
                    return value
                res.append(converted_val)
            return res
        return value

    def to_json(self, value: list) -> list:
        return [self._of_type.to_json(val) for val in value]

    def value_repr(self, value: list) -> str:
        if isinstance(self._of_type, (ObjectType, MappingType)) and value:
            return f'[...] ({len(value)} items)'
        return str(value)


class DictType(Type):
    _type = dict

    def __init__(self, keys: Type, values: Type):
        self._keys = keys
        self._values = values

    def __str__(self):
        return f'Dict[{str(self._keys)}, {str(self._values)}]'

    def validate(self, value: Any):
        super().validate(value)
        for key, val in value.items():
            self._keys.validate(key)
            self._values.validate(val)

    def _from_string(self, value: str) -> Union[dict, str]:
        try:
            return json.loads(value.replace("'", '"'))
        except json.JSONDecodeError:
            return value

    def convert(self, value: Any) -> Any:
        converted_value = super().convert(value)
        if isinstance(converted_value, dict):
            res = {}
            for key, val in converted_value.items():
                converted_key = self._keys.convert(key)
                converted_val = self._values.convert(val)
                try:
                    self._keys.validate(converted_key)
                    self._values.validate(converted_val)
                except ValueError:
                    return value
                res[converted_key] = converted_val
            return res
        return value

    def to_json(self, value: dict) -> dict:
        return {self._keys.to_json(k): self._values.to_json(v)
                for k, v in value.items()}

    def value_repr(self, value: dict) -> str:
        if isinstance(self._values, (ObjectType, MappingType)) and value:
            return f'{{...}} ({len(value)} items)'
        return str(value)


class DateTimeType(Type):
    _type = datetime
    _format = '%Y-%m-%dT%H:%M:%SZ'

    def _from_string(self, value: str) -> Union[datetime, str]:
        modified_value = re.sub(r'\..*Z', r'Z', value)
        try:
            return datetime.strptime(modified_value, self._format)
        except ValueError:
            return value

    def to_json(self, value: datetime) -> str:
        return datetime.strftime(value, self._format)


class ObjectType(Type):
    """
    Type representing some custom, user-defined class.
    It is assumed that objects of this class can be fully instantiated
    with a dict containing all the needed data.

    Example:

    .. code-block:: python

        >>> class Foo:
        ...     def __init__(self, a, b):
        ...         self.a = a
        ...         self.b = b
        ...
        ...     def __repr__(self):
        ...         return f'<Foo a={self.a}, b={self.b} />'

        >>> type_ = ObjectType(Foo)
        >>> type_.convert({'a': 123, 'b': 'bar'})
        <Foo a=123, b=bar />

    """

    def __init__(self, class_: TypingType[T]):
        self._type = class_

    def __str__(self):
        return str(self._type.__name__)

    def _from_string(self, value: str) -> T:
        raise NotImplementedError

    def convert(self, value: Any) -> T:
        if isinstance(value, dict):
            return self._type(**value)
        return value

    def to_json(self, value: T) -> Dict[str, Any]:
        return value.to_json()  # type: ignore[attr-defined]

    def value_repr(self, value: T) -> str:
        return f'<{self._type.__name__} ...>'


class MappingType(Type):
    """
    Type representing some kind of mapping. It is used to determine the
    correct type of the object at runtime, depending on the specified
    field.

    Example:

    .. code-block:: python

        >>> class Foo:
        ...     def __init__(self, a, type):
        ...         self.a = a
        ...         self.type = type
        ...
        ...     def __repr__(self):
        ...         return f'<Foo a={self.a} />'

        >>> class Bar:
        ...     def __init__(self, a, b, c, type):
        ...         self.abc = f'{a}{b}{c}'
        ...         self.type = type
        ...
        ...     def __repr__(self):
        ...         return f'<Bar abc={self.abc} />'

        >>> type_ = MappingType('type', {
        ...     'foo': ObjectType(Foo),
        ...     'bar': ObjectType(Bar),
        ... })

        >>> type_.convert({'type': 'foo', 'a': 123})
        <Foo a=123 />

        >>> type_.convert({'type': 'bar', 'a': 'a', 'b': 'b', 'c': 42})
        <Bar abc=ab42 />

        >>> foo = Foo(a=123, type='foo')
        >>> type_.validate(foo)

        >>> foo = Foo(a=123, type='bar')
        >>> type_.validate(foo)
        Traceback (most recent call last):
        ...
        ValueError

    """

    def __init__(self, mapping_key: str, mapping: Dict[str, ObjectType]):
        self._mapping_key = mapping_key
        self._mapping = mapping

    def __str__(self):
        types = ', '.join(type_ for type_ in self._mapping)
        return f'Union[{types}]'

    def convert(self, value: Any) -> Any:
        if isinstance(value, dict):
            key = value.get(to_camel_case(self._mapping_key), '')
            type_ = self._mapping.get(key)
            if not type_:
                return value
            return type_.convert(value)
        raise value

    def validate(self, value: Any):
        key = getattr(value, self._mapping_key, None)
        type_ = self._mapping.get(key)
        if not type_:
            raise ValueError
        type_.validate(value)

    def to_json(self, value: Any) -> Dict[str, Any]:
        return value.to_json()

    def value_repr(self, value: Any) -> str:
        key = getattr(value, self._mapping_key, None)
        type_ = self._mapping.get(key)
        if not type_:
            raise ValueError
        return type_.value_repr(value)


def new_type(type_: Type) -> Callable[[], Type]:
    return lambda: type_


NumericType = new_type(UnionType(IntegerType(), FloatType()))
