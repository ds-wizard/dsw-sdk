"""
Module with classes procuring the whole authentication process.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict

import jwt
import requests
from requests.auth import AuthBase

from dsw_sdk.http_client.interface import UnexpectedAuthError


AUTH_ERROR = 'There is no token in authentication response. ' \
             'Please, contact the API maintainer.'
INVALID_TOKEN_ERROR = 'Authentication token is invalid. ' \
                      'Please, contact the API maintainer.'


class TokenRetrievalStrategy:
    """
    Abstract class for strategy on how to retrieve auth token from the server.

    Every subclass has to implement the :meth:`get_new_token` method.
    """
    def __init__(self, auth_url: str, credentials: Dict[str, str]):
        """
        :param auth_url: URL of the authentication endpoint
        :param credentials: dict containing keys ``email`` and ``password``
        """
        self._url = auth_url
        self._credentials = credentials

    def get_new_token(self) -> str:
        """
        Make a POST request to the authentication URL and obtain new auth
        token.

        :raises: :exc:`requests.HTTPError` on HTTP status codes between 400
                 and 599
        :raises: :exc:`~interface.UnexpectedAuthError` on missing token in
                 HTTP response body

        :return: authentication token to be passed with every request
        """
        raise NotImplementedError


class BodyTokenRetrievalStrategy(TokenRetrievalStrategy):
    """
    This strategy knows how to retrieve an authentication token
    contained in the body of the HTTP response from the server.
    """
    def get_new_token(self) -> str:
        response = requests.post(self._url, json=self._credentials)
        response.raise_for_status()
        new_token = response.json().get('token')
        if not new_token:
            raise UnexpectedAuthError(AUTH_ERROR)
        return new_token


class BearerAuth(AuthBase):
    """
    Subclass of :class:`requests.AuthBase`, defining how to authenticate with
    every request via the Bearer authentication protocol defined in RFC 6750.
    """
    def __init__(self, token: str):
        """
        :param token: Authentication token obtained from the auth endpoint
        """
        self._token = token

    def __call__(
        self,
        r: requests.PreparedRequest,
    ) -> requests.PreparedRequest:
        r.headers['Authorization'] = f'Bearer {self._token}'
        return r


class JWTBearerAuth(BearerAuth):
    """
    Subclass of :class:`requests.AuthBase`, defining how to authenticate
    with every request using JSON Web Tokens defined in RFC 7519.
    """
    def __init__(self, token_retrieval_strategy: TokenRetrievalStrategy):
        """
        :param token_retrieval_strategy: means of authentication
        """
        super().__init__('')
        self._token_retrieval_strategy = token_retrieval_strategy

    def __call__(
        self,
        r: requests.PreparedRequest,
    ) -> requests.PreparedRequest:
        now_with_padding = datetime.now() + timedelta(seconds=30)
        if (
            not self._token
            or self.token_expiration(self._token) <= now_with_padding
        ):
            self._token = self._token_retrieval_strategy.get_new_token()
        return super().__call__(r)

    @staticmethod
    def token_expiration(jwt_token) -> datetime:
        """
        Return expiration datetime of given ``jwt_token``.

        :param jwt_token: string representation of a JWT token (encoded)

        :raises: :exc:`~interface.UnexpectedAuthError` if
                 ``jwt_token`` is not a valid JWT token

        :return: datetime of expiration
        """
        try:
            # We won't verify the signature as we do
            # not have the secret from the server.
            jwt_claims = jwt.decode(
                jwt_token,
                options={'verify_signature': False},
            )
        except jwt.DecodeError as err:
            raise UnexpectedAuthError(INVALID_TOKEN_ERROR) from err
        exp = jwt_claims.get('exp', 0)
        return datetime.fromtimestamp(exp)
