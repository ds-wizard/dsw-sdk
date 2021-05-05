# type: ignore[override]
"""
Module containing the base Model class along with it's utility classes.
Also defining two attributes, specific for the Model subclasses only.
"""
from __future__ import annotations

from typing import Any, Dict, NoReturn, Type

from dsw_sdk.common.attributes import (
    AttributesMixin,
    ListAttribute,
    ObjectAttribute,
    StringAttribute,
)
from dsw_sdk.common.snapshot import (
    Snapshot,
    make_snapshot,
    snapshots_diff,
)
from dsw_sdk.common.types import ObjectType


class AlreadyRemovedError(Exception):
    """
    Exception raised when trying to save (via :meth:`Model.save` method) an
    already deleted model (the method :meth:`Model.delete` was called).
    """
    msg = 'Model `{}` was already removed and cannot be updated anymore.'

    def __init__(self, model: Model):
        """
        :param model: Instance of a model that has been deleted
        """
        super().__init__(self.msg.format(model))


class State:
    """
    Base class for all other states of the model creating
    a state machine (state design pattern).
    """
    __slots__ = ()

    def save(self, model: Model) -> State:
        """
        According to a current state, does whatever is appropriate
        for saving the entity.
        Must be implemented in every subclass.

        :param model: model to perform the "save" operation on
        :return: instance of the next state
        """
        raise NotImplementedError

    def delete(self, model: Model) -> State:
        """
        According to a current state, does whatever is appropriate
        for removing the entity.
        Must be implemented in every subclass.

        :param model: model to perform the "delete" operation on
        :return: instance of the next state
        """
        raise NotImplementedError


class NewState(State):
    """
    State of an entity that does not yet exist on the server, but an
    instance of a corresponding model is already created.
    """

    def save(self, model: Model) -> State:
        """
        Creates new entity on the server.

        :param model: model to perform the "save" operation on
        :return: instance of class:`ExistingState` class
        """
        model._create()
        return ExistingState()

    def delete(self, model: Model) -> State:
        """
        Does nothing as the entity doesn't really exist.

        :param model: model to perform the "delete" operation on
        :return: instance of class:`DeletedState` class
        """
        return DeletedState()


class ExistingState(State):
    """
    State of an entity that exists on the server.
    """

    def save(self, model: Model) -> State:
        """
        Updates the entity on the server.

        :param model: model to perform the "save" operation on
        :return: self
        """
        model._update()
        return self

    def delete(self, model: Model) -> State:
        """
        Removes the entity on the server.

        :param model: model to perform the "delete" operation on
        :return: instance of class:`DeletedState` class
        """
        model._delete()
        return DeletedState()


class DeletedState(State):
    """
    State of an entity that was on the server, but has been deleted
    and now exists only an instance of a corresponding model.
    """
    def save(self, model: Model) -> NoReturn:
        """
        This *always* raises an :class:`AlreadyRemovedError` exception
        as it is invalid operation. Cannot update an entity that does
        not exist anymore.

        :param model: model to perform the "save" operation on

        :raises: :exc:`AlreadyRemovedError` always
        """
        raise AlreadyRemovedError(model)

    def delete(self, model: Model) -> State:
        """
        Does nothing as the entity is already deleted on the server.

        :param model: model to perform the "delete" operation on
        :return: self
        """
        return self


class Model(AttributesMixin):
    """
    This is the base class for all the data stewardship wizard data entities.
    Defines the one attribute that is common for all entities -- UUID.

    It tracks it's own state and according to this state it can decide, which
    operation to do when calling the :meth:`save` and :meth:`delete` methods.

    For tracking of changes, snapshots (:class:`Snapshot` class) are used.

    It also modifies a behavior of it's parent, :class:`AttributesMixin`
    class -- when the attribute is not yet set, it does not raise. Instead
    ``None`` value is returned.

    If you, for some reason, want to just create a model for an entity that
    already exists on the server and you have all the required data, do:

    .. code-block:: python

        # 1
        >>> model = Model(None, __update_attrs={'uuid': '123'})
        >>> model.uuid
        '123'

        # 2
        >>> model = Model(None)
        >>> model._update_attrs(uuid='123')
        >>> model.uuid
        '123'

    In either case, the model will be set with correct state.
    """
    uuid: str = StringAttribute(read_only=True)

    def __init__(self, sdk, **kwargs):
        """
        :param sdk: instance of the :class:`DataStewardshipWizardSDK` class
        :param kwargs: arbitrary attributes that can be set on this entity
        """
        self._sdk = sdk
        self._state = NewState()
        self._snapshot = Snapshot({})
        super().__init__(**kwargs)

    def __repr__(self):
        # Displaying the UUID in order to quickly identify the entity but
        # keeping the representation (e.g. in lists) still compact
        return f'<{self.__class__.__name__} uuid="{self.uuid}" ...>'

    def __getattr__(self, item: str):
        """
        :meth:`__getattr__` is invoked when the attribute ``item`` is not
        found via standard lookup mechanism. Two scenarios are possible:

            1) The ``item`` is defined on the class via descriptor, but the
               descriptor raised an exception. This means that the attribute
               was not yet set on the model and we return ``None``.

            2) The ``item`` does not exist on the class at all. In this case
               we should behave like any normal object, i.e. raise an
               ``AttributeError`` exception.

        :param item: name of the attribute that was requested
        :return: ``None``

        :raises: :exc:`AttributeError` if the attribute does not exist
                 on this entity
        """
        if item in self.attr_names:
            return None
        raise AttributeError(f'`{self}` object has no attribute `{item}`')

    def _update_attrs(self, **kwargs):
        super()._update_attrs(**kwargs)
        # The entity already exists, we must set the correct state
        self._state = ExistingState()
        # And make snapshot of the current state
        # to start tracking changes from now on
        self._snapshot = make_snapshot(self)

    def _create(self):
        """
        Performs all actions to create an entity on the server.
        Must be implemented by every subclass.
        """
        raise NotImplementedError

    def _update(self):
        """
        Performs all actions to update an entity on the server.
        Must be implemented by every subclass.
        """
        raise NotImplementedError

    def _delete(self):
        """
        Performs all actions to delete an entity on the server.
        Must be implemented by every subclass.
        """
        raise NotImplementedError

    def save(self):
        """
        If there are some changes to save, persist them on the server.
        It will either create or update the entity, according to it's state.

        :raises: :exc:`AlreadyRemovedError` if the entity was already deleted
        """
        if snapshots_diff(self._snapshot, make_snapshot(self)):
            self._state = self._state.save(self)
            self._snapshot = make_snapshot(self)

    def delete(self):
        """
        Deletes the entity.
        Particular actions depend on entity's internal state.
        """
        self._state = self._state.delete(self)

    def attrs(self) -> Dict[str, Any]:
        """
        Gets all attributes with non-``None`` value.

        :return: dict with all entity's attributes,
                 excluding the ``None`` values
        """
        attrs = super().attrs()
        return {k: v for k, v in attrs.items() if v is not None}


class ModelAttribute(ObjectAttribute):
    """
    Attribute containing another :class:`Model` instance.
    """

    def __set__(self, instance: Model, value: Any):
        """
        If we are assigning a dict representation of the model
        we have to do 2 things:

            1) If the entity already exists on the server, we must
               just initialize the model with it's data, therefore
               passing the attributes as ``__update_attrs`` keyword.

            2) Each model needs an instance of the
               :class:`DataStewardshipWizardSDK` class. So we take
               it from the current entity and pack it up with other
               data.

        """
        if isinstance(value, dict):
            if 'uuid' in value:
                value = {'__update_attrs': value}
            value = {'sdk': instance._sdk, **value}
        super().__set__(instance, value)


class ListOfModelsAttribute(ListAttribute):
    """
    Attribute containing a list of another :class:`Model` instances.
    """

    def __init__(self, model_class: Type[Model], **kwargs):
        super().__init__(ObjectType(model_class), **kwargs)

    def __set__(self, instance: Model, value: Any):
        """
        Same as :class:`ModelAttribute`, except for list of values.
        """
        if isinstance(value, list):
            new_value = []
            for val in value:
                if isinstance(val, dict):
                    if 'uuid' in val:
                        val = {'__update_attrs': val}
                    val = {'sdk': instance._sdk, **val}
                new_value.append(val)
            value = new_value
        super().__set__(instance, value)
