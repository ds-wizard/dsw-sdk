import datetime

import jwt
import mock
import pytest
import requests
from pytest_data import get_data, use_data

from dsw_sdk.http_client.requests_impl.auth import (
    AUTH_ERROR,
    BearerAuth,
    BodyTokenRetrievalStrategy,
    INVALID_TOKEN_ERROR,
    JWTBearerAuth,
)
from dsw_sdk.http_client.interface import UnexpectedAuthError


# ---------------------------- Fixtures and mocks ----------------------------


class TokenResponse:
    def __init__(self, token, raises=False):
        self._token = token
        self._raises = raises

    def json(self):
        return {'token': self._token}

    def raise_for_status(self):
        if self._raises:
            raise requests.HTTPError('Something went terribly wrong')


@pytest.fixture
def mocked_request():
    return mock.Mock(headers={})


@pytest.fixture
def jwt_token_expiration(request):
    jwt_token_data = get_data(
        request,
        'jwt_token_data',
        {'expiration_in': datetime.timedelta(seconds=1)},
    )
    expiration = datetime.datetime.now() + jwt_token_data['expiration_in']
    return expiration.timestamp()


@pytest.fixture
def jwt_token(jwt_token_expiration):
    return jwt.encode(
        {'some': 'payload', 'exp': jwt_token_expiration},
        'secret',
        algorithm='HS256',
    )


@pytest.fixture
def requests_mock(request, jwt_token):
    requests_mock_data = get_data(
        request,
        'requests_mock_data',
        {'auth_response': TokenResponse(jwt_token)},
    )
    auth_response = requests_mock_data['auth_response']
    with mock.patch(
        'dsw_sdk.http_client.requests_impl.auth.requests.post',
        return_value=auth_response
    ) as requests_mock:
        yield requests_mock


@pytest.fixture
def strategy_mock(request, jwt_token):
    mock_data = get_data(
        request,
        'token_retrieval_strategy_data',
        {'return_value': jwt_token, 'side_effect': None},
    )
    mock_ = mock.MagicMock()
    mock_.get_new_token.return_value = mock_data['return_value']
    mock_.get_new_token.side_effect = mock_data['side_effect']
    return mock_


@pytest.fixture
def strategy():
    return BodyTokenRetrievalStrategy(
        'auth_url',
        {'email': '', 'password': ''},
    )


# -------------------------- Token retrieval classes -------------------------


def test_body_token_retrieval_strategy(strategy, requests_mock, jwt_token):
    assert strategy.get_new_token() == jwt_token


@use_data(
    requests_mock_data={'auth_response': TokenResponse(..., raises=True)},
)
def test_body_token_retrieval_strategy_http_error(strategy, requests_mock):
    with pytest.raises(requests.HTTPError):
        strategy.get_new_token()


@use_data(requests_mock_data={'auth_response': TokenResponse(None)})
def test_body_token_retrieval_strategy_missing_token(strategy, requests_mock):
    with pytest.raises(UnexpectedAuthError) as e:
        strategy.get_new_token()
    assert e.match(AUTH_ERROR)


# -------------------------------- Auth classes ------------------------------


def test_bearer_auth(mocked_request):
    auth = BearerAuth('some random token')
    assert auth(mocked_request).headers == {
        'Authorization': 'Bearer some random token',
    }


@use_data(jwt_token_data={'expiration_in': datetime.timedelta(seconds=-123)})
def test_jwt_bearer_token_expiration(jwt_token, jwt_token_expiration):
    # We are also testing that decoding expired JWT token won't result
    # in exception (thanks to `verify_signature=False` option)
    expiration = JWTBearerAuth.token_expiration(jwt_token).timestamp()
    assert expiration == jwt_token_expiration


def test_jwt_bearer_token_with_no_expiration():
    jwt_token = jwt.encode({'some': 'payload'}, 'secret', algorithm='HS256')
    expiration = JWTBearerAuth.token_expiration(jwt_token)
    # Comparing dates and not datetimes, because depending on what your local
    # time zone is, `datetime.datetime.fromtimestamp(0)` can return different
    # results
    assert expiration.date() == datetime.date(1970, 1, 1)


def test_jwt_bearer_token_error():
    with pytest.raises(UnexpectedAuthError) as e:
        JWTBearerAuth.token_expiration('invalid.jwt.token')
    assert e.match(INVALID_TOKEN_ERROR)


def test_jwt_bearer_auth(jwt_token, mocked_request, strategy_mock):
    auth = JWTBearerAuth(strategy_mock)
    assert auth(mocked_request).headers == {
        'Authorization': f'Bearer {jwt_token}',
    }
    assert strategy_mock.get_new_token.call_count == 1


@use_data(jwt_token_data={'expiration_in': datetime.timedelta(seconds=30)})
def test_jwt_bearer_auth_with_expired_token(
    jwt_token,
    mocked_request,
    strategy_mock,
):
    """
    Check that expired token gets replaced and the ``get_new_token`` is
    called every single time.
    """
    auth = JWTBearerAuth(strategy_mock)
    for _ in range(10):
        auth(mocked_request)
    assert strategy_mock.get_new_token.call_count == 10


@use_data(jwt_token_data={'expiration_in': datetime.timedelta(hours=1)})
def test_jwt_bearer_auth_with_fresh_token(
    jwt_token,
    mocked_request,
    strategy_mock,
):
    """
    Check that token is requested only once (at the beginning) if the
    token isn't expired.
    """
    auth = JWTBearerAuth(strategy_mock)
    for _ in range(10):
        auth(mocked_request)
    assert strategy_mock.get_new_token.call_count == 1


@use_data(
    token_retrieval_strategy_data={
        'side_effect': UnexpectedAuthError(AUTH_ERROR),
    },
)
def test_jwt_bearer_auth_with_missing_token(
    jwt_token,
    mocked_request,
    strategy_mock,
):
    auth = JWTBearerAuth(strategy_mock)
    with pytest.raises(UnexpectedAuthError) as e:
        auth(mocked_request)
    assert e.match(AUTH_ERROR)


@use_data(token_retrieval_strategy_data={'side_effect': requests.HTTPError()})
def test_jwt_bearer_auth_with_http_error(
    jwt_token,
    mocked_request,
    strategy_mock,
):
    auth = JWTBearerAuth(strategy_mock)
    with pytest.raises(requests.HTTPError):
        auth(mocked_request)
