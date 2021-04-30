import mock
import pytest
import requests
from pytest_data import get_data, use_data, use_data_parametrize

from dsw_sdk.http_client.requests_impl.http_client import SessionHttpClient
from dsw_sdk.http_client.interface import HttpError, NotFoundError


DEFAULT_TIMEOUT = (6.05, 27)


class HttpErrorResponse:
    def raise_for_status(self):
        mocked_response = mock.Mock(status_code=400)
        mocked_response.json.return_value = {'message': 'Bad request'}
        raise requests.HTTPError(
            'Something went wrong',
            response=mocked_response,
        )


class NotFoundErrorResponse:
    def raise_for_status(self):
        mocked_response = mock.Mock(status_code=404)
        mocked_response.json.return_value = {
            'message': {'defaultMessage': 'X: %s, Y: %s', 'params': [1, 2]}
        }
        raise requests.HTTPError(
            'Something went wrong',
            response=mocked_response,
        )


class HttpClientWithBeforeRequest(SessionHttpClient):
    def before_request(self, *args, **kwargs):
        new_args = (*args, 'some_new_argument')
        new_kwargs = {**kwargs, 'new_keyword': 'argument'}
        return new_args, new_kwargs


class HttpClientWithAfterRequest(SessionHttpClient):
    def after_request(self, response):
        response.some_attribute_modified_in_after_request = 42
        return response


@pytest.fixture
def session_mock(request):
    session_data = get_data(request, 'session_mock_data', {'auth': None})
    session_mock = mock.Mock(**session_data)
    return session_mock


@pytest.fixture
def logger_mock():
    return mock.Mock()


@pytest.fixture
def http_method_mock(request, logger_mock):
    data = get_data(request, 'mocked_method_data', {'method': 'get'})
    method = data.pop('method')

    client = SessionHttpClient('base_url', mock.Mock(), logger_mock,
                               default_timeout=DEFAULT_TIMEOUT)
    with mock.patch.object(client._session, method, **data) as method_mock:
        method_mock.__name__ = method
        yield method_mock, getattr(client, method)


def test_no_request_is_made_on_init():
    SessionHttpClient(
        'completely invalid URL that would fail if any request was made',
        ...,
        ...,
    )


@use_data(
    session_mock_data={
        'headers': {'some': 'headers'},
        'verify': False,
        'auth': 'Some auth',
    },
)
def test_user_can_provide_own_session(session_mock):
    client = SessionHttpClient(
        'base_url',
        mock.Mock(),
        mock.Mock(),
        session=session_mock,
    )
    assert client._session == session_mock
    assert client._session.headers == {'some': 'headers'}
    assert client._session.verify is False
    assert client._session.auth == 'Some auth'

    session_mock.auth = None
    auth_class_mock = mock.Mock()
    client = SessionHttpClient(
        'base_url',
        auth_class_mock,
        mock.Mock(),
        session=session_mock,
    )
    assert client._session.auth == auth_class_mock


def test_user_can_set_default_headers():
    client = SessionHttpClient('base_url', mock.Mock(), mock.Mock())
    assert client._session.headers['Accept'] == '*/*'

    client = SessionHttpClient(
        'base_url',
        mock.Mock(),
        mock.Mock(),
        headers={'some': 'headers', 'Accept': 'application/xml'},
    )
    assert client._session.headers['some'] == 'headers'
    assert client._session.headers['Accept'] == 'application/xml'


@use_data_parametrize(http_method_mock=[
    {'method': 'head'},
    {'method': 'options'},
    {'method': 'get'},
    {'method': 'post'},
    {'method': 'put'},
    {'method': 'delete'},
])
def test_http_methods(http_method_mock):
    method_mock, method_func = http_method_mock
    method_func('/some_endpoint', some='keyword', arguments=[(), (1, 2)])

    kwargs = {
        'timeout': DEFAULT_TIMEOUT,
        'some': 'keyword',
        'arguments': [(), (1, 2)],
    }
    if method_func.__name__ in ('post', 'put'):
        kwargs = {'json': None, **kwargs}

    assert method_mock.call_count == 1
    method_mock.assert_called_with('base_url/some_endpoint', **kwargs)


@use_data_parametrize(http_method_mock=[
    {'method': 'head'},
    {'method': 'options'},
    {'method': 'get'},
    {'method': 'post'},
    {'method': 'put'},
    {'method': 'delete'},
])
def test_http_methods_logging(http_method_mock, logger_mock):
    method_mock, method_func = http_method_mock
    method_func('/some_endpoint', some='keyword', arguments=[(), (1, 2)])

    kwargs = {
        'some': 'keyword',
        'arguments': [(), (1, 2)],
    }
    if method_func.__name__ in ('post', 'put'):
        kwargs = {'json': None, **kwargs}
    logger_args = logger_mock.info.call_args_list

    assert logger_mock.info.call_count == 2
    assert (
        logger_args[0].args[0]
        ==
        f'Starting {method_func.__name__.upper()} request to `/some_endpoint` '
        f'with arguments: `()` and `{kwargs}`.'
    )
    assert logger_args[1].args[0].startswith('Request finished. Took about ')


@use_data_parametrize(http_method_mock=[
    {'method': 'head', 'return_value': HttpErrorResponse()},
    {'method': 'options', 'return_value': HttpErrorResponse()},
    {'method': 'get', 'return_value': HttpErrorResponse()},
    {'method': 'post', 'return_value': HttpErrorResponse()},
    {'method': 'put', 'return_value': HttpErrorResponse()},
    {'method': 'delete', 'return_value': HttpErrorResponse()},
])
def test_http_error(http_method_mock):
    _, method_func = http_method_mock
    with pytest.raises(HttpError):
        method_func('/some_endpoint')


@use_data(mocked_method_data={
    'method': 'get', 'return_value': NotFoundErrorResponse(),
})
def test_not_found_error(http_method_mock):
    _, method_func = http_method_mock
    with pytest.raises(NotFoundError) as e:
        method_func('/some_endpoint')
    assert e.value.status_code == 404
    assert e.value.msg == 'X: 1, Y: 2'


@pytest.mark.parametrize('method', [
    'head', 'options', 'get', 'post', 'put', 'delete',
])
def test_before_request(method):
    client = HttpClientWithBeforeRequest('base_url', mock.Mock(), mock.Mock())
    with mock.patch.object(client._session, method) as method_mock:
        method_mock.__name__ = method
        method_func = getattr(client, method)
        method_func('/endpoint')
        assert method_mock.call_count == 1
        assert 'some_new_argument' in method_mock.call_args.args
        assert method_mock.call_args.kwargs['new_keyword'] == 'argument'


@pytest.mark.parametrize('method', [
    'head', 'options', 'get', 'post', 'put', 'delete',
])
def test_after_request(method):
    client = HttpClientWithAfterRequest('base_url', mock.Mock(), mock.Mock())
    with mock.patch.object(client._session, method) as method_mock:
        method_mock.__name__ = method
        method_func = getattr(client, method)
        res = method_func('/endpoint')
        assert method_mock.call_count == 1
        assert res.some_attribute_modified_in_after_request == 42
