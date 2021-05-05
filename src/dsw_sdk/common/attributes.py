"""
Core module for working with attributes. Defines two important classes
:class:`AttributesMixin` (attributes container) and :class:`Attribute`.
Also defining all different kinds of specific attributes.

When designing this library, there was a need to implement some kind of
mechanism, that would allow following:

    * Easy definition of data entities and their attributes, including
      their type, default value, range and whether they are immutable or
      read-only. This should be done in as declarative and concise form
      as possible.
    * Validation and possible conversion of values when assigning to
      these attributes.
    * Possibility to initialize the whole entity either in one step
      (passing all the values to the ``__init__`` method) or gradually
      by assigning one attribute at a time.
    * There must be a way to initialize the entity without any validation.

Because of these requirements, I decided to implement the attribute as a
descriptor. It allows for concise and clean definition and we can specify
any custom logic we want when assigning a value, while keeping simple dot
notation (``obj.attribute = 1``).

:class:`AttributesMixin` is just a container for these descriptors,
containing all the methods to ease the usage of it's subclasses.
"""

from __future__ import annotations

import inspect
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
    """
    Raised when accessing an attribute that was not yet set.
    """
    msg = 'You must set the `{}` parameter'

    def __init__(self, name: str):
        super().__init__(self.msg.format(name))


class AttributesNotSetError(AttributeNotSetError):
    """
    Raised if there are some attributes that were not yet set
    when validating an :class:`AttributesMixin` instance.
    """
    msg = 'You must set following parameters: {}'

    def __init__(self, params: List[str]):
        super().__init__(', '.join(params))


class ReadOnlyAccessError(AttributeError):
    """
    Raised when assigning value to a read-only attribute.
    """
    msg = 'Attribute `{}` is read only'

    def __init__(self, name: str):
        super().__init__(self.msg.format(name))


class ModifyImmutableError(AttributeError):
    """
    Raised when assigning value to an immutable attribute that
    already has some value set.
    """
    msg = 'Attribute `{}` is immutable - once set, it cannot be changed.'

    def __init__(self, name: str):
        super().__init__(self.msg.format(name))


class InvalidValueError(ValueError):
    """
    Raised if validation failed when assigning to an attribute.
    """
    msg = f'{INVALID_VALUE} of type `{{}}`'

    def __init__(self, value: Any, name: str, type_: Type):
        super().__init__(self.msg.format(value, name, type_))


class NotInChoicesError(ValueError):
    """
    Raised if value assigned to an attribute is not in
    specified range of values.
    """
    msg = f'{INVALID_VALUE}, expected one of `{{}}`'

    def __init__(self, value: Any, name: str, choices: Sequence[Any]):
        super().__init__(self.msg.format(value, name, choices))


class AttributesMixin:
    """
    Container for :class:`Attribute` instances. This class should not
    be used directly, instead it should be subclassed and have some
    attributes defined.

    Note that if you try to retrieve an attribute that was not yet
    set and it does not have any default value, an exception will
    be raised.

    Example usage:

    .. code-block:: python

        >>> class Foo(AttributesMixin):
        ...     some_attr = BoolAttribute(immutable=True)
        ...     bar = IntegerAttribute(choices=(1, 2))

        # Passing attribute values when creating object
        >>> foo = Foo(some_attr=False)
        >>> foo.some_attr
        False

        >>> foo.some_attr = True
        Traceback (most recent call last):
        ...
        dsw_sdk.common.attributes.ModifyImmutableError: ...

        >>> foo.bar
        Traceback (most recent call last):
        ...
        dsw_sdk.common.attributes.AttributeNotSetError: ...

        >>> foo.bar = 1
        >>> foo.bar = 'two'
        Traceback (most recent call last):
        ...
        dsw_sdk.common.attributes.InvalidValueError: ...

        >>> foo.bar = 3
        Traceback (most recent call last):
        ...
        dsw_sdk.common.attributes.NotInChoicesError: ...

        # Use `_update_attrs` to skip validations
        of `read_only` and `immutable` flags
        >>> foo._update_attrs(some_attr=True)
        >>> foo.some_attr
        True
    """
    # Define list of attributes that should not be taken
    # into account when comparing two instances
    _eq_ignore: List[str] = []

    def __init__(self, **kwargs):
        """
        :param kwargs: All the attributes you want to set on this instance.
                       Note that the attribute must be defined on the class,
                       otherwise it won't get assigned.
                       Attributes passed as a dict in ``_update_attrs``
                       keyword argument skip validation of `read_only` and
                       `immutable` flags.
        """
        self._attrs: Dict[str, Any] = {}
        self._with_validations = True
        self._attr_descriptors: Dict[str, Attribute] = {}
        self._attr_names: List[str] = []

        # Set all attributes passed as kwargs
        for attr_name, attr in kwargs.items():
            if to_snake_case(attr_name) in self.attr_names:
                setattr(self, to_snake_case(attr_name), attr)

        if kwargs.get('__update_attrs'):
            self._update_attrs(**kwargs['__update_attrs'])

    def __repr__(self):
        return f'<{self.__class__.__name__} ...>'

    def __str__(self):
        """
        If there are less than 4 attributes, the instance is represented as:

            <ClassName attr1=value1 attr2=value2 >

        Otherwise it looks something like:

            <ClassName
              attr1=value1
              attr2=value2
            >
        """
        attrs = ''
        sep = '\n  ' if len(self.attrs()) > 3 else ' '
        for key, val in self.attrs().items():
            attrs += f'{sep}{key}={self._attr_to_str(key, val)}'
        return f'<{self.__class__.__name__} {attrs}{sep[0]}>'

    def __eq__(self, other):
        """
        Just comparing all the attributes (including
        default values) set on both instances.
        """
        if self.__class__ != other.__class__:
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
        """
        Returns descriptor instance for a given attribute name.
        """
        return self._get_attr_descriptors()[name]

    def _attr_to_str(self, name: str, value: Any) -> str:
        desc = self._get_attr_descriptor(name)
        return desc.value_repr(value)

    def _get_attr_descriptors(self) -> Dict[str, Attribute]:
        """
        Collects all attributes (their descriptors) starting from
        current class up to this class (:class:`AttributesMixin`).

        Thanks to this, we can define hierarchical structures of
        classes with attributes (with inheritance).
        """
        if not self._attr_descriptors:
            # The last two base classes will always be `AttributeMixin`
            # (this class) and the `object` class, so we can skip them
            classes = inspect.getmro(self.__class__)[:-2]
            # Reversing order as we want the general classes first and then
            # the more specific ones. That's because some classes may override
            # the original attribute definition and we want the most specific
            # definition at the end.
            for class_ in reversed(classes):
                values = class_.__dict__.values()
                attrs = filter(lambda v: isinstance(v, Attribute), values)
                self._attr_descriptors.update({attr.name: attr
                                               for attr in attrs})
        return self._attr_descriptors

    @property
    def attr_names(self) -> List[str]:
        """
        List of all attributes names defined on
        this class and all of it's superclasses.

        :return: names of all attributes
        """
        if not self._attr_names:
            # Sorting the names just to make the classes
            # with a lot of attributes easier to read
            self._attr_names = sorted(self._get_attr_descriptors().keys())
        return self._attr_names

    def attrs(self) -> Dict[str, Any]:
        """
        Collects all attribute values set on this instance,
        including default values of attributes and returns
        them as ``dict`` (keys are the attributes names).

        :return: ``dict`` with attribute names and corresponding values
        """
        res = {}
        # We want also default values, that's why we
        # don't just return the `self._attrs` value
        for attr_name in self.attr_names:
            try:
                res[attr_name] = getattr(self, attr_name)
            except AttributeNotSetError:
                pass
        return res

    def validate(self):
        """
        Validates if all attributes that are needed (i.e. they don't have
        the ``nullable`` flag set) are set. If not, raises an exception.

        :raises: :exc:`AttributesNotSetError` if there are
                 some attributes needed to be set
        """
        errors = []
        for attr_name in self.attr_names:
            try:
                getattr(self, attr_name)
            except AttributeNotSetError:
                errors.append(attr_name)
        if errors:
            raise AttributesNotSetError(errors)

    def to_json(self) -> Dict[str, Any]:
        """
        Converts the whole instance (it's attributes) to JSON
        representation.
        Useful for serializing the instance's state.

        :return: dict representation of all the attributes and their values
        """
        return {
            name: attr.to_json(getattr(self, name))
            for name, attr in self._get_attr_descriptors().items()
        }

    def _update_attrs(self, **kwargs):
        """
        This method enables assigning values to attributes without
        validating the `read_only` and `immutable` flags.

        This is useful when you define some attributes that shouldn't
        be edited by users, but you have to initialize these values
        somehow.

        :param kwargs: all the attributes you want to set, same
                       as ``kwargs`` in :meth:`__init__` method

        :raises: :exc:`ReadOnlyAccessError` if setting `read-only`
                 attribute
        :raises: :exc:`ModifyImmutableError` if modifying `immutable`
                 attribute that was already set
        :raises: :exc:`InvalidValueError` if the value given
                 for the attribute is of invalid type
        :raises: :exc:`NotInChoicesError` if the value given
                 for the attribute is not in the defined range
        """
        self._with_validations = False
        for key, value in kwargs.items():
            setattr(self, to_snake_case(key), value)
        self._with_validations = True


class Attribute:
    """
    Class representing one attribute on the :class:`AttributesMixin`
    classes.

    It's defined as a data descriptor, responsible for validating
    values when the assignment takes place.

    For example usage, see :class:`AttributesMixin`, as these two
    can't be really used separately.
    """

    def __init__(self, type_: Type, **kwargs):
        """
        :param `type_`: type of the attribute

        :Keyword arguments:
            * **default** (`Any`): default value for the attribute
            * **nullable** (`bool`): whether ``None`` should be a valid value
            * **read_only** (`bool`): if set to ``True``, assigning to this
              attribute will raise an exception
            * **immutable** (`bool`): if set to ``True``, it's possible to
              assign a value to this attribute only once; any other try will
              raise an exception
            * **choices** (`Sequence[Any]`): sequence defining range of
              possible values
        """
        default = kwargs.get('default', NOT_SET)
        if kwargs.get('nullable'):
            type_ = UnionType(NoneType(), type_)
            default = None if default == NOT_SET else default
        self._type = type_
        self._default = default
        self._read_only = kwargs.get('read_only', False)
        self._immutable = kwargs.get('immutable', False)
        self._choices = kwargs.get('choices')

    def __set_name__(self, owner: TypingType, name: str):
        self.name = name  # pylint: disable=W0201

    def __get__(self, instance: AttributesMixin, owner: TypingType) -> Any:
        """
        Returns the attribute's value, if set. If not, check for a
        default value, otherwise raise an exception.
        """
        value = instance._attrs.get(self.name, self._default)
        # Using `NOT_SET` sentinel and not e.g. `None`, because even
        # `None` can be used as valid default value.
        if value == NOT_SET:
            raise AttributeNotSetError(self.name)
        return value

    def __set__(self, instance: AttributesMixin, value: Any):
        """
        This method is responsible for all the validations when
        assigning value to an attribute.
        """
        if instance._with_validations and self._read_only:
            raise ReadOnlyAccessError(self.name)

        if (
            instance._with_validations
            and self._immutable
            and self.name in instance._attrs
            and instance._attrs[self.name] != value
        ):
            raise ModifyImmutableError(self.name)

        value = self._type.convert(value)
        try:
            self._type.validate(value)
        except ValueError:
            raise InvalidValueError(value, self.name, self._type)

        if self._choices is not None and value not in self._choices:
            raise NotInChoicesError(value, self.name, self._choices)

        instance._attrs[self.name] = value

    def to_json(self, value: Any) -> Any:
        """
        Returns JSON representation of given ``value``
        for the ``self._type`` data type.

        :param value: value to be converted

        :return: JSON representation of the ``value``
        """
        if value is None:
            return None
        return self._type.to_json(value)

    def value_repr(self, value: Any) -> str:
        """
        Returns string representation of given ``value``
        for the ``self._type`` data type.

        :param value: value to be represented as a string

        :return: string representing ``value``
        """
        return self._type.value_repr(value)


class StringAttribute(Attribute):
    def __init__(self, **kwargs):
        super().__init__(StringType(), **kwargs)


class IntegerAttribute(Attribute):
    def __init__(self, **kwargs):
        super().__init__(IntegerType(), **kwargs)


class FloatAttribute(Attribute):
    def __init__(self, **kwargs):
        super().__init__(FloatType(), **kwargs)


class BoolAttribute(Attribute):
    def __init__(self, **kwargs):
        super().__init__(BoolType(), **kwargs)


class ListAttribute(Attribute):
    def __init__(self, type_: Type, **kwargs):
        super().__init__(ListType(type_), **kwargs)


class DictAttribute(Attribute):
    def __init__(self, key_type: Type, value_type: Type, **kwargs):
        super().__init__(DictType(key_type, value_type), **kwargs)


class DateTimeAttribute(Attribute):
    def __init__(self, **kwargs):
        super().__init__(DateTimeType(), **kwargs)


class ObjectAttribute(Attribute):
    def __init__(self, type_: TypingType[AttributesMixin], **kwargs):
        super().__init__(ObjectType(type_), **kwargs)

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
