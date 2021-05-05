"""
Module containing a synchronous implementation of the
:class:`~interface.HttpClient`
interface via the popular `requests` library.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Callable, Dict, Tuple, Union

import requests
from requests.auth import AuthBase

from dsw_sdk.http_client.interface import (
    BadRequestError,
    ForbiddenError,
    HttpClient,
    HttpError,
    HttpResponse,
    NotFoundError,
)


class RequestsHttpResponse(HttpResponse):
    """
    Requests implementation of the :class:`~interface.HttpResponse` interface.
    """

    def __init__(self, response: requests.Response):
        """
        :param response: original :class:`requests.Response` object
        """
        self._response = response

    @property
    def path(self) -> str:
        return self._response.request.path_url

    @property
    def orig_response(self) -> Any:
        return self._response

    @property
    def text(self) -> str:
        return self._response.text

    def json(self, **kwargs) -> Dict[str, Any]:
        return self._response.json(**kwargs)


class SessionHttpClient(HttpClient):
    """
    HTTP client for easy communication with the Data Stewardship Wizard API.
    It's a synchronous implementation of a :class:`~interface.HttpClient`
    interface via the ``Requests`` package.

    Uses :class:`requests.Session` in order to re-use HTTP connections and
    improve overall performance. Also transparently mediates the authentication
    process.

    It is possible to add custom logic with :meth:`before_request` and
    :meth:`after_request` hooks.

    All requests raise :class:`~interface.HttpError`, so you don't have to
    check every response for valid status code. Just assume it's OK and catch
    the aforementioned exception somewhere.
    The :class:`~interface.UnexpectedAuthError` is raised if some unexpected
    error occurs during the authentication process. This means the API
    responded in an unexpected way and something is wrong.

    :Keyword arguments:
        * **default_timeout**:
            This timeout is used as default value when no timeout is specified
            within a request. You can pass one numeric value (applied for both
            the connect and read timeouts), tuple of numeric values to specify
            different connect and read timeouts or ``None`` to wait forever.
            Default: ``None``.
        * **session** (`requests.Session`):
            If you want, you can configure your own session (instance of a
            :class:`requests.Session` class) outside of this client and pass
            it as keyword argument.
        * **headers**: (`Dict[str, str]`)
            Dict of all the HTTP headers you want to send with each requests.
        * **enable_ssl** (`bool`):
            If you set this flag to ``True``, every request gets encrypted and
            the whole communication will be done over SSL/TLS.
            Default: ``True``.
    """

    def __init__(self, base_url: str, auth_class: AuthBase,
                 logger: logging.Logger, **kwargs):
        """
        :param base_url: URL of the DSW API
        :param auth_class: class responsible for the authentication process
        :param logger: logger object
        """
        super().__init__(base_url, auth_class, logger, **kwargs)
        self._base_url = base_url
        self._logger = logger
        self._default_timeout = kwargs.get('default_timeout')

        self._session = kwargs.get('session') or requests.Session()
        self._session.headers.update(kwargs.get('headers') or {})
        if not kwargs.get('session'):
            self._session.verify = kwargs.get('enable_ssl', True)
        if not self._session.auth:
            self._session.auth = auth_class

    def before_request(  # pylint: disable=R0201
        self,
        *args,
        **kwargs
    ) -> Tuple[Tuple[Any, ...], Dict[str, Any]]:
        """
        This method can be overridden by users to provide custom logic before
        sending the request.

        ``args`` and ``kwargs`` are the exact arguments that go into the
        request. This method must return the same, new or modified ``args``
        and ``kwargs``.

        :return: current, new or modified positional and keyword arguments
                 for the request
        """
        return args, kwargs

    def after_request(  # pylint: disable=R0201
        self,
        response: RequestsHttpResponse,
    ) -> RequestsHttpResponse:
        """
        This method can be overridden by users to provide custom logic after
        receiving the response.

        ``response`` is the original response from the server. This
        method must return the same, new or modified response.

        :param response: original response from the server

        :return: current, new or modified response from the server
        """
        return response

    def _request(self, func: Callable, path: Union[str, bytes],
                 *args, **kwargs) -> RequestsHttpResponse:
        """
        General method for performing an HTTP request to the DSW API. Each
        request invokes the ``self._session.auth`` class and thus perform the
        authentication. Also call :meth:`before_request` and
        :meth:`after_request` hooks.

        :param func: function from the :mod:`requests` module to perform the
                     HTTP request
        :param path: path part of the URL

        :raises: :exc:`~interface.HttpError` on HTTP status codes between 400
                 and 599 while authenticating or doing the request itself
        :raises: :exc:`~interface.UnexpectedAuthError` on unexpected errors
                 while authenticating

        :return: HTTP response, possibly modified by the
                 :meth:`after_request` hook
        """
        args, kwargs = self.before_request(*args, **kwargs)

        method = func.__name__.upper()
        self._logger.info(f'Starting {method} request to `{path}` with '
                          f'arguments: `{args}` and `{kwargs}`.')
        start_time = time.time()

        try:
            res = func(f'{self._base_url}{path}', *args,
                       timeout=self._default_timeout, **kwargs)
            res.raise_for_status()
        except requests.HTTPError as err:
            resp = RequestsHttpResponse(err.response)
            if err.response.status_code == 400:
                raise BadRequestError(resp)
            if err.response.status_code == 403:
                raise ForbiddenError(resp)
            if err.response.status_code == 404:
                raise NotFoundError(resp)
            raise HttpError(err.response.status_code, resp) from err

        self._logger.info(f'Request finished. Took about '
                          f'{time.time() - start_time:.2f} seconds.')
        res = self.after_request(RequestsHttpResponse(res))
        return res

    def head(self, path: str, **kwargs) -> RequestsHttpResponse:
        """
        Sends a HEAD request. Returns :class:`RequestsHttpResponse` object.

        :param path: path for the new :class:`requests.Request` object.
        :param kwargs: Optional arguments that the request takes.

        :raises: :exc:`~interface.HttpError` on HTTP status codes between 400
                 and 599 while authenticating or doing the request itself
        :raises: :exc:`~interface.UnexpectedAuthError` on unexpected errors
                 while authenticating
        """
        return self._request(self._session.head, path, **kwargs)

    def options(self, path: str, **kwargs) -> RequestsHttpResponse:
        """
        Sends an OPTIONS request. Returns :class:`RequestsHttpResponse` object.

        :param path: path for the new :class:`requests.Request` object.
        :param kwargs: Optional arguments that the request takes.

        :raises: :exc:`~interface.HttpError` on HTTP status codes between 400
                 and 599 while authenticating or doing the request itself
        :raises: :exc:`~interface.UnexpectedAuthError` on unexpected errors
                 while authenticating
        """
        return self._request(self._session.options, path, **kwargs)

    def get(self, path: str, **kwargs) -> RequestsHttpResponse:
        """
        Sends a GET request. Returns :class:`RequestsHttpResponse` object.

        :param path: path for the new :class:`requests.Request` object.
        :param kwargs: Optional arguments that request takes.

        :raises: :exc:`~interface.HttpError` on HTTP status codes between 400
                 and 599 while authenticating or doing the request itself
        :raises: :exc:`~interface.UnexpectedAuthError` on unexpected errors
                 while authenticating
        """
        return self._request(self._session.get, path, **kwargs)

    def post(self, path: str, body: Dict[str, Any] = None,
             **kwargs) -> RequestsHttpResponse:
        """
        Sends a POST request. Returns :class:`RequestsHttpResponse` object.

        :param path: path for the new :class:`requests.Request` object.
        :param body: (optional) json to send in the body of the
                     :class:`requests.Request`.
        :param kwargs: Optional arguments that the request takes.

        :raises: :exc:`~interface.HttpError` on HTTP status codes between 400
                 and 599 while authenticating or doing the request itself
        :raises: :exc:`~interface.UnexpectedAuthError` on unexpected errors
                 while authenticating
        """
        return self._request(self._session.post, path, json=body, **kwargs)

    def put(self, path: str, body: Dict[str, Any] = None,
            **kwargs) -> RequestsHttpResponse:
        """
        Sends a PUT request. Returns :class:`RequestsHttpResponse` object.

        :param path: path for the new :class:`requests.Request` object.
        :param body: (optional) json to send in the body of the
                     :class:`requests.Request`.
        :param kwargs: Optional arguments that the request takes.

        :raises: :exc:`~interface.HttpError` on HTTP status codes between 400
                 and 599 while authenticating or doing the request itself
        :raises: :exc:`~interface.UnexpectedAuthError` on unexpected errors
                 while authenticating
        """
        return self._request(self._session.put, path, json=body, **kwargs)

    def delete(self, path: str, **kwargs) -> RequestsHttpResponse:
        """
        Sends a DELETE request. Returns :class:`RequestsHttpResponse` object.

        :param path: path for the new :class:`requests.Request` object.
        :param kwargs: Optional arguments that the request takes.

        :raises: :exc:`~interface.HttpError` on HTTP status codes between 400
                 and 599 while authenticating or doing the request itself
        :raises: :exc:`~interface.UnexpectedAuthError` on unexpected errors
                 while authenticating
        """
        return self._request(self._session.delete, path, **kwargs)
