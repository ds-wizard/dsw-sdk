import mock
import pytest
from pytest_data import get_data, use_data

from dsw_sdk.common.attributes import StringAttribute
from dsw_sdk.high_level_api.models.model import (
    AlreadyRemovedError,
    ExistingState,
    DeletedState,
    ListOfModelsAttribute,
    Model,
    ModelAttribute,
    NewState,
)


def modified(return_val: bool):
    return mock.patch(
        'dsw_sdk.high_level_api.models.model.snapshots_diff',
        return_value=return_val,
    )


class Foo(Model):
    some_attr = StringAttribute()
    another_attr = StringAttribute()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._create = mock.Mock()
        self._update = mock.Mock()
        self._delete = mock.Mock()

    def __str__(self):
        return 'Test Model'


@pytest.fixture
def new_model(request):
    data = get_data(request, 'new_model_data', {})
    return Foo(..., **data)


@pytest.fixture
def loaded_model(request):
    data = get_data(request, 'loaded_model_data', {})
    return Foo(..., __update_attrs=data)


# -------------------------- Tests of Model class ----------------------------


def test_model_not_set_attr():
    model = Model(...)
    assert model.uuid is None


def test_model_non_existing_attr():
    model = Model(...)
    with pytest.raises(AttributeError) as e:
        _ = model.bla
    assert e.match(f'`{model}` object has no attribute `bla`')


def test_model_equality_with_uuid():
    test1 = Foo(..., __update_attrs={'uuid': '1234'}, some_attr=123)
    test2 = Foo(..., __update_attrs={'uuid': '1234'}, some_attr=123)
    assert test1 == test2

    test1 = Foo(..., __update_attrs={'uuid': '1234'}, some_attr=123)
    test2 = Foo(..., __update_attrs={'uuid': '1234'}, some_attr=False)
    assert test1 != test2

    test1 = Foo(..., __update_attrs={'uuid': '1234'})
    test2 = Foo(..., __update_attrs={'uuid': '4321'})
    assert test1 != test2


def test_new_model_init_state(new_model):
    assert isinstance(new_model._state, NewState)


@use_data(loaded_model_data={'uuid': '12-ab', 'some_attr': 'foo'})
def test_loaded_model_init_state(loaded_model):
    assert isinstance(loaded_model._state, ExistingState)


@mock.patch(
    'dsw_sdk.high_level_api.models.model.snapshots_diff',
    return_value=False,
)
def test_model_state_after_save(_, new_model):
    assert isinstance(new_model._state, NewState)
    assert new_model._create.call_count == 0
    assert new_model._update.call_count == 0

    with modified(True):
        new_model.save()
    assert isinstance(new_model._state, ExistingState)
    assert new_model._create.call_count == 1
    assert new_model._update.call_count == 0

    # Calling it without modifications won't do anything
    new_model.save()
    assert isinstance(new_model._state, ExistingState)
    assert new_model._create.call_count == 1
    assert new_model._update.call_count == 0

    # Pretend that some modifications was made
    with modified(True):
        new_model.save()
    assert isinstance(new_model._state, ExistingState)
    assert new_model._create.call_count == 1
    assert new_model._update.call_count == 1

    new_model._state = DeletedState()
    with modified(True), pytest.raises(AlreadyRemovedError) as e:
        new_model.save()
    assert e.match('Model `Test Model` was already removed '
                   'and cannot be updated anymore.')


def test_model_state_after_delete(new_model):
    assert isinstance(new_model._state, NewState)
    assert new_model._delete.call_count == 0

    new_model.delete()
    assert isinstance(new_model._state, DeletedState)
    assert new_model._delete.call_count == 0

    new_model._state = ExistingState()
    new_model.delete()
    assert isinstance(new_model._state, DeletedState)
    assert new_model._delete.call_count == 1

    # Calling it multiple times doesn't matter
    new_model.delete()
    assert isinstance(new_model._state, DeletedState)
    assert new_model._delete.call_count == 1


@use_data(loaded_model_data={'uuid': '1'})
def test_model_attrs(loaded_model):
    assert loaded_model.attrs() == {'uuid': '1'}

    loaded_model.some_attr = '123'
    assert loaded_model.attrs() == {'uuid': '1', 'some_attr': '123'}


@use_data(loaded_model_data={'uuid': 'ab65nc'})
def test_model_save_with_error(loaded_model):
    loaded_model._update.side_effect = RuntimeError

    loaded_model.some_attr = 'abc bla'
    with pytest.raises(RuntimeError):
        loaded_model.save()

    assert loaded_model.some_attr == 'abc bla'
    assert isinstance(loaded_model._state, ExistingState)


# ----------------------- Tests of Attributes classes ------------------------

def test_model_attribute():
    class TestModel(Model):
        model_attr = ModelAttribute(Foo)

    mocked_sdk = mock.Mock()
    test_model = TestModel(mocked_sdk, model_attr={'some_attr': '123'})
    assert isinstance(test_model.model_attr, Foo)
    assert test_model.model_attr._sdk is mocked_sdk


def test_list_of_models_attribute():
    class TestModel(Model):
        list_of_models = ListOfModelsAttribute(Foo)

    mocked_sdk = mock.Mock()
    test_model = TestModel(mocked_sdk)
    test_model.list_of_models = [{'some_attr': '123'}, {'some_attr': 'foo'}]

    assert len(test_model.list_of_models) == 2
    assert isinstance(test_model.list_of_models[0], Foo)
    assert isinstance(test_model.list_of_models[1], Foo)
    assert test_model.list_of_models[0]._sdk is mocked_sdk
    assert test_model.list_of_models[1]._sdk is mocked_sdk
