import mock
import pytest
from pytest_data import get_data, use_data

from dsw_sdk.common.attributes import (
    Attribute,
    AttributeNotSetError,
    AttributesMixin,
    AttributesNotSetError,
    InvalidValueError,
    ModifyImmutableError,
    NotInChoicesError,
    ReadOnlyAccessError,
)


def get_descriptor(instance, desc_name='some_attr'):
    # Using `vars` to obtain the descriptor from class without triggering it
    return vars(instance.__class__)[desc_name]


@pytest.fixture
def test_class(request, mocked_type):
    data = get_data(request, 'test_class_data', {'attrs': {}})
    attrs = data.pop('attrs')

    class Test(AttributesMixin):
        some_attr = Attribute(mocked_type, **data)
        another_attr = Attribute(mocked_type)
        third_attr = Attribute(mocked_type)

    test = Test()
    test._attrs = attrs
    return test


@pytest.fixture
def mocked_type():
    mock_ = mock.Mock()
    mock_.convert.side_effect = lambda value: value
    return mock_


# -------------------------- AttributesMixin tests ---------------------------


def test_attributes_mixin_init(mocked_type):
    class Test(AttributesMixin):
        some_attr = Attribute(mocked_type)

    test = Test(some_attr=1234, non_existing_attr='foo')
    assert test._attrs == {'some_attr': 1234}
    assert test.some_attr == 1234
    assert not hasattr(test, 'non_existing_attr')


def test_attributes_mixin_attr_names(test_class):
    assert test_class.attr_names == ['another_attr', 'some_attr', 'third_attr']


def test_attributes_mixin_attr_names_multiple_inheritance():
    class Test(AttributesMixin):
        some_attr = Attribute(mock.Mock())

    class Test2(Test):
        another_attr = Attribute(mock.Mock())

    class Test3(Test2):
        third_attr = Attribute(mock.Mock())

    assert Test().attr_names == ['some_attr']
    assert Test2().attr_names == ['another_attr', 'some_attr']
    assert Test3().attr_names == ['another_attr', 'some_attr', 'third_attr']


@use_data(test_class_data={'attrs': {'another_attr': 123}, 'default': True})
def test_attributes_mixin_attrs(test_class):
    assert test_class.attrs() == {'some_attr': True, 'another_attr': 123}


def test_attributes_mixin_attrs_multiple_inheritance(mocked_type):
    class Test(AttributesMixin):
        some_attr = Attribute(mocked_type)

    class Test2(Test):
        another_attr = Attribute(mocked_type)

    class Test3(Test2):
        third_attr = Attribute(mocked_type)

    assert Test(some_attr=123).attrs() == {'some_attr': 123}
    assert Test2(some_attr=123, another_attr=False).attrs() == {
        'another_attr': False,
        'some_attr': 123,
    }
    assert Test3(some_attr=123, another_attr=False, third_attr=None).attrs() == {
        'third_attr': None,
        'another_attr': False,
        'some_attr': 123,
    }


def test_attributes_mixin_type_inequality(mocked_type):
    class Test(AttributesMixin):
        some_attr = Attribute(mocked_type)

    class Another(AttributesMixin):
        some_attr = Attribute(mocked_type)

    test = Test(some_attr=1234)
    another = Another(some_attr=1234)

    assert test != another


def test_attributes_mixin_attribute_equality(mocked_type):
    class Test(AttributesMixin):
        some_attr = Attribute(mocked_type)

    test1 = Test(some_attr=1234)
    test2 = Test()
    test2.some_attr = 1234

    assert test1 == test2


def test_attributes_mixin_equality_ignore(mocked_type):
    class Test(AttributesMixin):
        _eq_ignore = ['ignored']

        some_attr = Attribute(mocked_type)
        ignored = Attribute(mocked_type)

    test1 = Test(some_attr=1234, ignored='foo')
    test2 = Test()
    test2.some_attr = 1234
    test2.ignored = 'bar'

    assert test1 == test2


def test_attributes_mixin_attribute_inequality(mocked_type):
    class Test(AttributesMixin):
        some_attr = Attribute(mocked_type)

    test1 = Test(some_attr=1234)
    test2 = Test(some_attr=[True, False, None])

    assert test1 != test2


@use_data(test_class_data={
    'attrs': {'some_attr': 123, 'another_attr': True, 'third_attr': []}
})
def test_attributes_mixin_to_json(test_class, mocked_type):
    test_class.to_json()
    assert mocked_type.to_json.call_count == 3
    assert mocked_type.to_json.mock_calls[0].args == (123,)
    assert mocked_type.to_json.mock_calls[1].args == (True,)
    assert mocked_type.to_json.mock_calls[2].args == ([],)


@use_data(test_class_data={'attrs': {'some_attr': 123}})
def test_attributes_mixin_to_json_fail(test_class):
    with pytest.raises(AttributeNotSetError) as e:
        test_class.to_json()
    assert e.match(e.value.msg.format('another_attr'))


@use_data(test_class_data={
    'attrs': {'some_attr': 123, 'another_attr': False, 'third_attr': None}
})
def test_attributes_mixin_validate(test_class):
    test_class.validate()


@use_data(test_class_data={'attrs': {'some_attr': None}})
def test_attributes_mixin_validate_fail(test_class):
    with pytest.raises(AttributesNotSetError) as e:
        test_class.validate()
    msg = AttributesNotSetError.msg.format('another_attr, third_attr')
    assert e.match(msg)


@use_data(test_class_data={'read_only': True})
def test_attributes_mixin_update_attrs(test_class):
    test_class._update_attrs(some_attr=123, non_existingAttr='foo')
    assert test_class.some_attr == 123
    assert test_class.non_existing_attr == 'foo'


def test_attributes_mixin_update_attrs_init(mocked_type):
    class Test(AttributesMixin):
        some_attr = Attribute(mocked_type, read_only=True)

    test = Test(__update_attrs={'some_attr': 'foo'})
    assert test.some_attr == 'foo'


# ---------------------------- Attribute tests -------------------------------


def test_attribute_init(test_class):
    assert get_descriptor(test_class)._name == 'some_attr'


@use_data(test_class_data={'attrs': {'some_attr': 1234}})
def test_get_attribute(test_class):
    assert test_class.some_attr == 1234


@use_data(test_class_data={'default': None})
def test_get_attribute_with_default(test_class):
    assert test_class.some_attr is None


def test_get_unset_attribute(test_class):
    with pytest.raises(AttributeNotSetError) as e:
        _ = test_class.some_attr
    assert e.match(e.value.msg.format('some_attr'))


def test_set_attribute(test_class, mocked_type):
    test_class.some_attr = True

    assert mocked_type.convert.call_count == 1
    assert mocked_type.convert.call_args.args[0] is True

    assert mocked_type.validate.call_count == 1
    assert mocked_type.validate.call_args.args[0] is True

    assert test_class.some_attr is True
    assert test_class._attrs['some_attr'] is True


@pytest.mark.parametrize('failing_method', ['validate', 'convert'])
def test_set_attribute_fail(test_class, mocked_type, failing_method):
    getattr(mocked_type, failing_method).side_effect = ValueError
    with pytest.raises(InvalidValueError) as e:
        test_class.some_attr = True
    assert e.match(e.value.msg.format(True, 'some_attr', mocked_type))


@use_data(test_class_data={'read_only': True})
def test_set_read_only_attribute(test_class):
    with pytest.raises(ReadOnlyAccessError) as e:
        test_class.some_attr = 'cannot be set'
    assert e.match(e.value.msg.format('some_attr'))


@use_data(test_class_data={'immutable': True})
def test_set_immutable_attribute(test_class):
    test_class.some_attr = 'first assigned value is OK'
    # Setting the same value is valid
    test_class.some_attr = 'first assigned value is OK'
    with pytest.raises(ModifyImmutableError) as e:
        test_class.some_attr = 'then the attribute is immutable'
    assert e.match(e.value.msg.format('some_attr'))


@use_data(test_class_data={'choices': (1, 2)})
def test_attribute_with_choices(test_class):
    test_class.some_attr = 1
    with pytest.raises(NotInChoicesError) as e:
        test_class.some_attr = 3
    assert e.value.args[0] == e.value.msg.format(3, 'some_attr', (1, 2))


@use_data(test_class_data={'nullable': True})
def test_nullable_attribute(test_class):
    assert test_class.some_attr is None
    test_class.some_attr = None
    assert test_class.some_attr is None
