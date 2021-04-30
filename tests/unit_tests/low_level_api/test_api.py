import mock
import pytest

from dsw_sdk.low_level_api.api import LowLevelAPI


@pytest.fixture
def http_client_mock():
    return mock.Mock()


@pytest.fixture
def low_level_api(http_client_mock):
    return LowLevelAPI(http_client_mock)


def test_method_with_query_params(http_client_mock, low_level_api):
    low_level_api.get_documents(query_params={
        'snake_case': 'par_ams',
        'nested': {'snake_case': 'par_ams'},
        'list': [{'snake_case': 1}, {'snake_case': 2}],
    })
    assert http_client_mock.get.call_count == 1
    http_client_mock.get.assert_called_with(
        '/documents',
        params={
            'snakeCase': 'par_ams',
            'nested': {'snakeCase': 'par_ams'},
            'list': [{'snakeCase': 1}, {'snakeCase': 2}],
        }
    )


def test_method_with_body(http_client_mock, low_level_api):
    low_level_api.post_users(body={
        'snake_case': 'par_ams',
        'nested': {'snake_case': 'par_ams'},
        'list': [{'snake_case': 1}, {'snake_case': 2}],
    })
    assert http_client_mock.post.call_count == 1
    http_client_mock.post.assert_called_with(
        '/users',
        body={
            'snakeCase': 'par_ams',
            'nested': {'snakeCase': 'par_ams'},
            'list': [{'snakeCase': 1}, {'snakeCase': 2}],
        }
    )
