import json
import re
from datetime import datetime
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Type as TypingType,
    TypeVar,
)

from dsw_sdk.common.utils import to_camel_case


T = TypeVar('T')


class Type:
    _type: TypingType

    def __str__(self):
        return str(self._type.__name__)

    def _from_string(self, value: str) -> Any:
        return value

    def validate(self, value: Any):
        if not type(value) == self._type:   # pylint: disable=C0123
            raise ValueError

    def convert(self, value: Any) -> Any:
        if isinstance(value, str):
            return self._from_string(value)
        return value

    def to_json(self, value: Any) -> Any:
        return value

    def value_repr(self, value: Any) -> str:
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

    def _from_string(self, value: str) -> None:  # pylint: disable=R1711
        if value.lower() not in ('none', 'null'):
            raise ValueError
        return None

    def convert(self, value: Any) -> Any:
        value = super().convert(value)
        if value is not None:
            raise ValueError
        return value


class BoolType(Type):
    _type = bool

    def _from_string(self, value: str) -> bool:
        value = value.lower()
        if value not in ('true', 'false'):
            raise ValueError
        return value.lower() == 'true'

    def convert(self, value: Any) -> Any:
        value = super().convert(value)
        if not isinstance(value, bool):
            raise ValueError
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
        # Converting to string first in order
        # not to convert bool or float values
        return int(str(value))


class FloatType(Type):
    _type = float

    def convert(self, value: Any) -> float:
        # Converting to string first in order not
        # to convert bool or integer values
        return float(str(value))


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

    def validate(self, value: Any):
        for type_ in self._of_types:
            try:
                type_.validate(value)
                return
            except ValueError:
                pass
        raise ValueError

    def convert(self, value: Any) -> Any:
        for type_ in self._of_types:
            try:
                return type_.convert(value)
            except ValueError:
                pass
        raise ValueError

    def to_json(self, value: Any) -> Any:
        for type_ in self._of_types:
            try:
                type_.validate(value)
                return type_.to_json(value)
            except ValueError:
                pass
        raise ValueError

    def value_repr(self, value: Any) -> str:
        for type_ in self._of_types:
            try:
                type_.validate(value)
                return type_.value_repr(value)
            except ValueError:
                pass
        raise ValueError


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

    def _from_string(self, value: str) -> List[str]:
        values = value.replace(' ', '').lstrip('(').rstrip(')').split(',')
        if self._of_types and len(values) != len(self._of_types):
            raise ValueError
        return values

    def convert(self, value: Any) -> tuple:
        value = super().convert(value)
        if isinstance(value, Iterable):
            return tuple(
                type_.convert(val) for val, type_ in zip(value, self._of_types)
            )
        raise ValueError

    def to_json(self, value: tuple) -> list:
        return [t.to_json(v) for v, t in zip(value, self._of_types)]

    def value_repr(self, value: tuple) -> str:
        if any(isinstance(type_, (ObjectType, MappingType)) for type_ in self._of_types) and value:
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
        value = super().convert(value)
        if isinstance(value, Iterable):
            return [self._of_type.convert(val) for val in value]
        raise ValueError

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

    def _from_string(self, value: str) -> dict:
        try:
            return json.loads(value.replace("'", '"'))
        except json.JSONDecodeError:
            raise ValueError

    def convert(self, value: Any) -> Any:
        value = super().convert(value)
        if isinstance(value, dict):
            return {
                self._keys.convert(k): self._values.convert(v)
                for k, v in value.items()
            }
        raise ValueError

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

    def _from_string(self, value: str) -> datetime:
        value = re.sub(r'\..*Z', r'Z', value)
        return datetime.strptime(value, self._format)

    def convert(self, value: Any) -> Any:
        value = super().convert(value)
        if not isinstance(value, datetime):
            raise ValueError
        return value

    def to_json(self, value: datetime) -> str:
        return datetime.strftime(value, self._format)


class ObjectType(Type):
    def __init__(self, class_: TypingType[T]):
        self._type = class_

    def __str__(self):
        return str(self._type.__name__)

    def _from_string(self, value: str) -> T:
        raise NotImplementedError

    def convert(self, value: Any) -> T:
        if isinstance(value, self._type):
            return value
        if isinstance(value, dict):
            return self._type(**value)
        raise ValueError

    def to_json(self, value: T) -> Dict[str, Any]:
        return value.to_json()

    def value_repr(self, value: T) -> str:
        return f'<{self._type.__name__} ...>'


class MappingType(Type):
    def __init__(self,  mapping_key: str, mapping: Dict[str, ObjectType]):
        self._mapping_key = mapping_key
        self._mapping = mapping

    def __str__(self):
        types = ', '.join(type_ for type_ in self._mapping)
        return f'Union[{types}]'

    def convert(self, value: Any) -> Any:
        if isinstance(value, dict):
            key = value.get(to_camel_case(self._mapping_key))
            type_ = self._mapping.get(key)
            if not type_:
                raise ValueError
            return type_.convert(value)
        raise ValueError

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
        return type_.value_repr(value)


def new_type(type_: Type) -> Callable[[], Type]:
    return lambda: type_


NumericType = new_type(UnionType(IntegerType(), FloatType()))
