import pytest
from pytest_data import use_data

from dsw_sdk.common.attributes import InvalidValueError, ReadOnlyAccessError
from dsw_sdk.high_level_api.models.model import AlreadyRemovedError
from dsw_sdk.high_level_api.models.user import User
from dsw_sdk.http_client.interface import NotFoundError


def test_get_one_user(dsw_sdk, user):
    loaded_user = dsw_sdk.users.get_user(user.uuid)

    assert loaded_user == user

    # Assert the presence of some attributes that are sent from the server
    assert loaded_user.created_at is not None
    assert loaded_user.updated_at is not None
    assert loaded_user.permissions is not None
    assert loaded_user.questionnaires == []


@use_data(users_data=[
    {'first_name': 'Many', 'email': 'john.doe@example.com'},
    {'first_name': 'Many', 'email': 'another@domain.hu'},
    {'first_name': 'Many different', 'email': 'zzz@email.org'},
])
def test_get_many_users(dsw_sdk, users):
    all_users = dsw_sdk.users.get_users()
    # There must be at least 4 users - one that we are using for the
    # whole testing and the other 3 we are creating in this test
    assert len(all_users) >= 4
    assert users[0] in all_users
    assert users[1] in all_users
    assert users[2] in all_users

    found_users = dsw_sdk.users.get_users(q='different')
    assert len(found_users) == 1
    assert found_users[0] == users[2]

    found_users = dsw_sdk.users.get_users(size=2)
    assert len(found_users) == 2

    found_users = dsw_sdk.users.get_users(sort='email,asc', q='Many')
    assert len(found_users) == 3
    assert found_users == sorted(users, key=lambda u: u.email)


def test_create_user_via_api(dsw_sdk, user_data):
    user = dsw_sdk.users.create_user(**user_data)
    assert user.uuid is not None


def test_create_user_via_object(dsw_sdk, user_data):
    user = User(dsw_sdk, **user_data)
    user.save()
    assert user.uuid is not None


def test_update_user(dsw_sdk, user):
    user.active = True
    user.affiliation = 'My University'
    user.role = 'admin'
    user.save()

    # We can save multiple times, it does not matter as it is idempotent
    user.save()
    user.save()

    assert user.active is True
    assert user.affiliation == 'My University'
    assert user.role == 'admin'

    with pytest.raises(ReadOnlyAccessError):
        user.image_url = 'some_url'

    with pytest.raises(InvalidValueError):
        user.active = None


def test_delete_user(dsw_sdk, user):
    user.delete()

    # We can delete multiple times, it does not matter as it is idempotent
    user.delete()
    user.delete()

    user.active = True
    with pytest.raises(AlreadyRemovedError):
        user.save()

    with pytest.raises(NotFoundError):
        dsw_sdk.users.get_user(user.uuid)


def test_delete_one_user(dsw_sdk, user):
    dsw_sdk.users.delete_user(user.uuid)
    with pytest.raises(NotFoundError):
        dsw_sdk.users.get_user(user.uuid)


@use_data(users_data=[
    {'first_name': 'xxx'},
    {'first_name': 'xxx'},
    {'first_name': 'xxx'},
])
def test_delete_many_users(dsw_sdk, users):
    users_cnt = len(dsw_sdk.users.get_users(q='xxx'))
    dsw_sdk.users.delete_users([user.uuid for user in users])
    assert len(dsw_sdk.users.get_users(q='xxx')) == users_cnt - 3
