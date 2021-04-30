import mock
import pytest

from dsw_sdk.common.attributes import AttributeNotSetError
from dsw_sdk.high_level_api.models.user import User


@pytest.fixture
def sdk_mock():
    create_response_mock = mock.Mock()
    create_response_mock.json.return_value = {}

    update_response_mock = mock.Mock()
    update_response_mock.json.return_value = {}

    mock_ = mock.Mock()
    mock_.api.post_users.return_value = create_response_mock
    mock_.api.put_user.return_value = update_response_mock

    return mock_


@pytest.fixture
def loaded_user(sdk_mock, user_data):
    return User(sdk_mock, __update_attrs={
        **user_data,
        'uuid': 'abc',
        'active': False,
    })


# ----------------------------------------------------------------------------


def test_user_create(dsw_sdk, user_data):
    user = User(dsw_sdk, **user_data)
    user.save()

    for key, value in user_data.items():
        # E-mail is randomized, so we must skip it, because there will
        # be different value each test, but e-mail in the saved cassette
        # stays the same.
        if key == 'email':
            continue
        assert getattr(user, key) == value
    assert user.active is False
    assert user.created_at is not None
    assert user.groups == []
    assert user.image_url is None
    assert user.permissions == ['PM_READ_PERM', 'QTN_PERM',
                                'DMP_PERM', 'SUBM_PERM']
    assert user.sources == ['internal']
    assert user.updated_at is not None
    assert user.questionnaires == []


def test_user_create_missing_attr(user_data):
    del user_data['email']
    user = User(..., **user_data)
    with pytest.raises(AttributeNotSetError) as e:
        user.save()
    assert e.match(e.value.msg.format('email'))


def test_user_update_password(sdk_mock, loaded_user):
    loaded_user.password = 'new_password'
    loaded_user.save()

    assert sdk_mock.api.put_user_password.call_count == 1
    assert sdk_mock.api.put_user.call_count == 0
    sdk_mock.api.put_user_password.assert_called_with(
        loaded_user.uuid,
        body={'password': 'new_password'},
    )


def test_user_update_not_password(sdk_mock, loaded_user):
    loaded_user.email = 'new.email@example.com'
    loaded_user.active = True
    loaded_user.role = 'data steward'
    loaded_user.save()

    assert sdk_mock.api.put_user_password.call_count == 0
    assert sdk_mock.api.put_user.call_count == 1
    assert sdk_mock.api.put_user.call_args.args == (loaded_user.uuid,)
    request_body = sdk_mock.api.put_user.call_args.kwargs['body']
    assert request_body['email'] == 'new.email@example.com'
    assert request_body['active'] is True
    assert request_body['role'] == 'data steward'


def test_user_update(sdk_mock, loaded_user):
    loaded_user.email = 'new.email@example.com'
    loaded_user.password = 'new_password'
    loaded_user.save()

    assert sdk_mock.api.put_user_password.call_count == 1
    assert sdk_mock.api.put_user.call_count == 1
    sdk_mock.api.put_user_password.assert_called_with(
        loaded_user.uuid,
        body={'password': 'new_password'},
    )
    assert sdk_mock.api.put_user.call_args.args == (loaded_user.uuid,)
    request_body = sdk_mock.api.put_user.call_args.kwargs['body']
    assert request_body['email'] == 'new.email@example.com'


def test_user_delete(sdk_mock, loaded_user):
    loaded_user.delete()
    assert sdk_mock.api.delete_user.call_count == 1
    sdk_mock.api.delete_user.assert_called_with(loaded_user.uuid)
