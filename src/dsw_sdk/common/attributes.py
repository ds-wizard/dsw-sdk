from __future__ import annotations

import inspect
from datetime import datetime
from typing import (
    Any,
    Dict,
    List,
    Sequence,
    Type as TypingType,
)

from dsw_sdk.common.types import (
    BoolType,
    DateTimeType,
    DictType,
    FloatType,
    IntegerType,
    ListType,
    NoneType,
    ObjectType,
    StringType,
    Type,
    UnionType,
)
from dsw_sdk.common.utils import to_snake_case


NOT_SET = '__not_set__'
INVALID_VALUE = 'Invalid value `{}` for attribute `{}`'


class AttributeNotSetError(AttributeError):
    msg = 'You must set the `{}` parameter'

    def __init__(self, name: str):
        super().__init__(self.msg.format(name))


class AttributesNotSetError(AttributeNotSetError):
    msg = 'You must set following parameters: {}'

    def __init__(self, params: List[str]):
        super().__init__(', '.join(params))


class ReadOnlyAccessError(AttributeError):
    msg = 'Attribute `{}` is read only'

    def __init__(self, name: str):
        super().__init__(self.msg.format(name))


class ModifyImmutableError(AttributeError):
    msg = 'Attribute `{}` is immutable - once set, it cannot be changed.'

    def __init__(self, name: str):
        super().__init__(self.msg.format(name))


class InvalidValueError(ValueError):
    msg = f'{INVALID_VALUE} of type `{{}}`'

    def __init__(self, value: Any, name: str, type_: Type):
        super().__init__(self.msg.format(value, name, type_))


class NotInChoicesError(ValueError):
    msg = f'{INVALID_VALUE}, expected one of `{{}}`'

    def __init__(self, value: Any, name: str, choices: Sequence[Any]):
        super().__init__(self.msg.format(value, name, choices))


class AttributesMixin:
    _eq_ignore: List[str] = []

    def __init__(self, **kwargs):
        self._attrs: Dict[str, Any] = {}
        self._with_validations = True

        for attr_name, attr in kwargs.items():
            if to_snake_case(attr_name) in self.attr_names:
                setattr(self, to_snake_case(attr_name), attr)

        if kwargs.get('__update_attrs'):
            self._update_attrs(**kwargs['__update_attrs'])

    def __repr__(self):
        return f'<{self.__class__.__name__} ...>'

    def __str__(self):
        attrs = ''
        sep = '\n  ' if len(self.attrs()) > 3 else ' '
        for key, val in self.attrs().items():
            attrs += f'{sep}{key}={self._attr_to_str(key, val)}'
        return f'<{self.__class__.__name__} {attrs}{sep[0]}>'

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        my_attrs = [v for k, v in self.attrs().items()
                    if k not in self._eq_ignore]
        other_attrs = [v for k, v in other.attrs().items()
                       if k not in self._eq_ignore]
        if len(my_attrs) != len(other_attrs):
            return False
        zipped_values = zip(my_attrs, other_attrs)
        for self_attr, other_attr in zipped_values:
            if self_attr != other_attr:
                return False
        return True

    def _get_attr_descriptor(self, name: str) -> Attribute:
        return self._get_attrs_descriptors()[name]

    def _attr_to_str(self, name: str, value: Any) -> str:
        desc = self._get_attr_descriptor(name)
        return desc.value_repr(value)

    def _get_attrs_descriptors(self) -> Dict[str, Attribute]:
        res = {}
        # The last two base classes will always be `AttributeMixin`
        # (this class) and the `object` class, so we can skip them
        classes = inspect.getmro(self.__class__)[:-2]
        for class_ in classes:
            values = class_.__dict__.values()
            attrs = filter(lambda v: isinstance(v, Attribute), values)
            res.update({attr._name: attr for attr in attrs})
        return res

    @property
    def attr_names(self) -> List[str]:
        # Sorting the names just to make the classes
        # with a lot of attributes easier to read
        return sorted(list(self._get_attrs_descriptors().keys()))

    def attrs(self) -> Dict[str, Any]:
        res = {}
        # We want also default values, that's why we
        # don't just return the `self._attrs` value
        for attr_name in self.attr_names:
            try:
                res.update({attr_name: getattr(self, attr_name)})
            except AttributeNotSetError:
                pass
        return res

    def validate(self):
        errors = []
        for attr_name in self.attr_names:
            try:
                getattr(self, attr_name)
            except AttributeNotSetError:
                errors.append(attr_name)
        if errors:
            raise AttributesNotSetError(errors)

    def to_json(self) -> Dict[str, Any]:
        res = {}
        for name, attr in self._get_attrs_descriptors().items():
            value = getattr(self, name)
            if value is None:
                res.update({name: None})
            else:
                res.update({name: attr._type.to_json(value)})
        return res

    def _update_attrs(self, **kwargs):
        self._with_validations = False
        for key, value in kwargs.items():
            setattr(self, to_snake_case(key), value)
        self._with_validations = True


class Attribute:
    def __init__(self, type_: Type, default: Any = NOT_SET,
                 nullable: bool = False, read_only: bool = False,
                 immutable: bool = False, choices: Sequence[Any] = None):
        if nullable:
            type_ = UnionType(NoneType(), type_)
            default = None if default == NOT_SET else default
        self._type = type_
        self._default = default
        self._read_only = read_only
        self._immutable = immutable
        self._choices = choices

    def __set_name__(self, owner: TypingType, name: str):
        self._name = name  # pylint: disable=W0201

    def __get__(self, instance: AttributesMixin, owner: TypingType) -> Any:
        value = instance._attrs.get(self._name, self._default)
        if value == NOT_SET:
            raise AttributeNotSetError(self._name)
        return value

    def __set__(self, instance: AttributesMixin, value: Any):
        if instance._with_validations and self._read_only:
            raise ReadOnlyAccessError(self._name)

        if (
            instance._with_validations
            and self._immutable
            and self._name in instance._attrs
            and instance._attrs[self._name] != value
        ):
            raise ModifyImmutableError(self._name)

        try:
            value = self._type.convert(value)
            self._type.validate(value)
        except ValueError:
            raise InvalidValueError(value, self._name, self._type)

        if self._choices is not None and value not in self._choices:
            raise NotInChoicesError(value, self._name, self._choices)

        instance._attrs[self._name] = value

    def value_repr(self, value: Any) -> str:
        return self._type.value_repr(value)


class StringAttribute(Attribute):
    def __init__(self, default: str = NOT_SET, nullable: bool = False,
                 read_only: bool = False, immutable: bool = False,
                 choices: Sequence[str] = None):
        super().__init__(StringType(), default, nullable,
                         read_only, immutable, choices)


class IntegerAttribute(Attribute):
    def __init__(self, default: int = NOT_SET, nullable: bool = False,
                 read_only: bool = False, immutable: bool = False,
                 choices: Sequence[int] = None):
        super().__init__(IntegerType(), default, nullable,
                         read_only, immutable, choices)


class FloatAttribute(Attribute):
    def __init__(self, default: float = NOT_SET, nullable: bool = False,
                 read_only: bool = False, immutable: bool = False,
                 choices: Sequence[float] = None):
        super().__init__(FloatType(), default, nullable,
                         read_only, immutable, choices)


class BoolAttribute(Attribute):
    def __init__(self, default: bool = NOT_SET, nullable: bool = False,
                 read_only: bool = False, immutable: bool = False,
                 choices: Sequence[bool] = None):
        super().__init__(BoolType(), default, nullable,
                         read_only, immutable, choices)


class ListAttribute(Attribute):
    def __init__(self, type_: Type, default: list = NOT_SET,
                 nullable: bool = False, read_only: bool = False,
                 immutable: bool = False, choices: Sequence[list] = None):
        super().__init__(ListType(type_), default, nullable,
                         read_only, immutable, choices)


class DictAttribute(Attribute):
    def __init__(self, key_type: Type, value_type: Type,
                 default: dict = NOT_SET, nullable: bool = False,
                 read_only: bool = False, immutable: bool = False,
                 choices: Sequence[dict] = None):
        super().__init__(DictType(key_type, value_type), default,
                         nullable, read_only, immutable, choices)


class DateTimeAttribute(Attribute):
    def __init__(self, default: datetime = NOT_SET, nullable: bool = False,
                 read_only: bool = False, immutable: bool = False,
                 choices: Sequence[datetime] = None):
        super().__init__(DateTimeType(), default, nullable,
                         read_only, immutable, choices)


class ObjectAttribute(Attribute):
    def __init__(self, type_: TypingType[AttributesMixin],
                 default: AttributesMixin = NOT_SET,
                 nullable: bool = False, read_only: bool = False,
                 immutable: bool = False,
                 choices: Sequence[AttributesMixin] = None):
        super().__init__(ObjectType(type_), default, nullable,
                         read_only, immutable, choices)

    def __set__(self, instance: AttributesMixin, value: Any):
        if isinstance(value, dict) and ('uuid' in value or 'id' in value):
            value = {'__update_attrs': value}
        super().__set__(instance, value)


class Alias:
    def __init__(self, aliased_attr: str):
        self._aliased_attr = aliased_attr

    def __get__(self, instance: AttributesMixin, value: Any) -> Any:
        return getattr(instance, self._aliased_attr)

    def __set__(self, instance: AttributesMixin, value: Any):
        setattr(instance, self._aliased_attr, value)
