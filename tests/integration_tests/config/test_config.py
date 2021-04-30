import os

import pytest
from pytest_data import get_data, use_data

from dsw_sdk.common.attributes import AttributeNotSetError, InvalidValueError
from dsw_sdk.config.config import Config, TIMEOUT_TYPE


CUR_DIR = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def set_env(request):
    data = get_data(request, 'set_env_data', {})
    os.environ.update(data)
    yield
    for key in data:
        del os.environ[key]


def test_empty_config():
    config = Config()
    assert config.http_client._attrs == {}


def test_basic_obj_config():
    config = Config(api_url='some_url', default_timeout=3.14)
    assert config.http_client.api_url == 'some_url'
    assert config.http_client.default_timeout == 3.14


def test_obj_config_fail():
    with pytest.raises(InvalidValueError) as e:
        Config(default_timeout=False)
    msg = e.value.msg.format('False', 'default_timeout', TIMEOUT_TYPE)
    assert e.value.args[0] == msg


def test_basic_file_config():
    config = Config(conf_file=f'{CUR_DIR}/test_config.yaml')
    assert config.http_client.enable_ssl is False
    assert config.http_client.auth_endpoint == '/tokens'
    assert config.http_client.headers == {'X-TEST-HEADER': 'TEST HEADER VALUE',
                                          'A': '1'}
    assert config.http_client.default_timeout == (6, 120)


@use_data(set_env_data={
    'DSW_SDK_EMAIL': 'e-mail',
    'DSW_SDK_HEADERS': '{"Connection": "close", "A": 0.14}',
})
def test_basic_env_config(set_env):
    config = Config()
    assert config.http_client.email == 'e-mail'
    assert config.http_client.headers == {'Connection': 'close', 'A': '0.14'}


@use_data(set_env_data={'DSW_SDK_ENABLE_SSL': 'maybe'})
def test_env_config_fail(set_env):
    with pytest.raises(InvalidValueError) as e:
        Config()
    assert e.match(e.value.msg.format('maybe', 'enable_ssl', 'bool'))


@use_data(set_env_data={
    'DSW_SDK_PASSWORD': 'password',
    'DSW_SDK_HEADERS': '{"Authorization": "Bearer X"}',
})
def test_combined_config(set_env):
    config = Config(conf_file=f'{CUR_DIR}/test_config.yaml',
                    enable_ssl=True, email='e-mail')
    # Values from file config
    assert config.http_client.auth_endpoint == '/tokens'
    assert config.http_client.default_timeout == (6, 120)
    # Values from env config
    assert config.http_client.password == 'password'
    assert config.http_client.headers == {'Authorization': 'Bearer X'}
    # Values from object config
    assert config.http_client.enable_ssl is True
    assert config.http_client.email == 'e-mail'


def test_default_values():
    config = Config()
    assert config.http_client.enable_ssl is True
    assert config.http_client.auth_endpoint == '/tokens'
    assert config.http_client.headers == {}
    assert config.http_client.default_timeout == (6.05, 27)


def test_missing_value():
    config = Config()
    with pytest.raises(AttributeNotSetError) as e:
        _ = config.http_client.api_url
    assert e.match(e.value.msg.format('api_url'))


def test_contains():
    config = Config(password='1234')
    assert 'password' in config.http_client
    assert 'email' not in config.http_client
    # Testing also attributes with default value
    assert 'auth_endpoint' in config.http_client


def test_get_item():
    config = Config(password='1234')
    assert config.http_client['password'] == '1234'
    # Testing also attributes with default value
    assert config.http_client['default_timeout'] == (6.05, 27)
    with pytest.raises(KeyError):
        _ = config.http_client['api_url']


def test_iter():
    config_data = {'password': '1234', 'auth_endpoint': 'some_uri'}
    default_data = {'enable_ssl': True, 'headers': {},
                    'default_timeout': (6.05, 27)}
    config = Config(**config_data)
    for key in config.http_client:
        assert key in {**config_data, **default_data}.keys()
    for k, v in config.http_client.items():
        assert k in {**config_data, **default_data}.keys()
        assert {**config_data, **default_data}[k] == v


def test_len():
    # There are 2 default attributes and 3 user defined
    config = Config(api_url='/', headers={}, enable_ssl=True)
    assert len(config.http_client) == 5


def test_kwargs_passing():
    def foo(**kwargs):
        assert kwargs['api_url'] == 'some_url'
        assert kwargs['default_timeout'] == (1, 2)
    config = Config(api_url='some_url', default_timeout=(1, 2))
    foo(**config.http_client)
