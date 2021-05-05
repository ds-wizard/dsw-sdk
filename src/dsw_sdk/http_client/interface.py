"""
General interfaces for HTTP communication -- HTTP client, HTTP response and
exceptions related to the whole process.
"""
from __future__ import annotations

import json
from typing import Any, Dict


class HttpResponse:
    """
    Object representing basic HTTP response that is passed across this SDK.
    Offers only basic methods, but the original response has to be always
    accessible via the :meth:`orig_response` property.
    """
    @property
    def path(self) -> str:
        raise NotImplementedError

    @property
    def orig_response(self) -> Any:
        raise NotImplementedError

    @property
    def text(self) -> str:
        raise NotImplementedError

    def json(self, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError


class HttpError(Exception):
    """
    General HTTP error occurring while communicating with the DSW API.
    Contains HTTP status code, error message and error response from the
    server.
    """
    _default_msg = 'Http error'

    def __init__(self, status_code: int, response: HttpResponse):
        self.status_code = status_code
        self.msg = self._get_message(response)
        self.response = response
        super().__init__(self.msg)

    def __str__(self):
        return f'[{self.status_code}] {self.msg} ({self.response.path})'

    @classmethod
    def _get_message(cls, response: HttpResponse) -> str:
        """
        Based on a content of the ``response``, extracts the error message.
        """
        try:
            resp = response.json()
        except json.JSONDecodeError:
            return response.text

        response_keys = ('message', 'error')
        msg = cls._default_msg

        for key in response_keys:
            if key not in resp:
                continue
            if 'defaultMessage' in resp[key] and 'params' in resp[key]:
                text = resp[key]['defaultMessage']
                params = tuple(resp[key]['params'])
                msg = text % params
            else:
                msg = resp[key]

        return msg


class BadRequestError(HttpError):
    """
    HTTP error with status code 400 Bad request.
    Client sent some invalid request to the server.
    """
    _default_msg = 'Bad request'

    def __init__(self, response: HttpResponse):
        super().__init__(400, response)


class ForbiddenError(HttpError):
    """
    HTTP error with status code 403 Forbidden.
    Client is not authorized to perform such request.
    """
    _default_msg = 'Forbidden'

    def __init__(self, response: HttpResponse):
        super().__init__(403, response)


class NotFoundError(HttpError):
    """
    HTTP error with status code 404 Not found.
    Client requested a resource that was not found on the server.
    """
    _default_msg = 'Not found'

    def __init__(self, response: HttpResponse):
        super().__init__(404, response)


class UnexpectedAuthError(Exception):
    """
    Something unexpected happened when performing the authentication. There
    may be something wrong with the DSW API or it could be just some temporary
    malfunction.
    """


class HttpClient:
    """
    General interface for any HTTP client responsible for communication with
    the DSW API.

    It does not make any assumptions on how the implementation should work or
    which libraries it should leverage. So if you want implement some client
    that is not shipped with this SDK (e.g. for asynchronous communication) or
    you want to use different libraries for HTTP stuff, feel free to subclass
    this interface and pass an instance of your client to the SDK when the
    initialization goes on.
    """

    def __init__(self, *args, **kwargs):
        pass

    def head(self, path: str, **kwargs) -> HttpResponse:
        """
        Sends a HEAD HTTP request.

        :param path: path for the request
        :param kwargs: Optional arguments that the request takes

        :raises: :exc:`HttpError` on HTTP status codes between 400 and 599
                 while authenticating or doing the request itself
        :raises: :exc:`UnexpectedAuthError` on unexpected errors while
                 authenticating

        :return: a response from the server contained
                 in the :class:`HttpResponse` object.
        """
        raise NotImplementedError

    def options(self, path: str, **kwargs) -> HttpResponse:
        """
        Sends a OPTIONS HTTP request.

        :param path: path for the request
        :param kwargs: Optional arguments that the request takes

        :raises: :exc:`HttpError` on HTTP status codes between 400 and 599
                 while authenticating or doing the request itself
        :raises: :exc:`UnexpectedAuthError` on unexpected errors while
                 authenticating

        :return: a response from the server contained
                 in the :class:`HttpResponse` object.
        """
        raise NotImplementedError

    def get(self, path: str, **kwargs) -> HttpResponse:
        """
        Sends a GET HTTP request.

        :param path: path for the request
        :param kwargs: Optional arguments that the request takes

        :raises: :exc:`HttpError` on HTTP status codes between 400 and 599
                 while authenticating or doing the request itself
        :raises: :exc:`UnexpectedAuthError` on unexpected errors while
                 authenticating

        :return: a response from the server contained
                 in the :class:`HttpResponse` object.
        """
        raise NotImplementedError

    def post(self, path: str, body: Dict[str, Any] = None,
             **kwargs) -> HttpResponse:
        """
        Sends a POST HTTP request.

        :param path: path for the request
        :param body: body of the request
        :param kwargs: Optional arguments that the request takes

        :raises: :exc:`HttpError` on HTTP status codes between 400 and 599
                 while authenticating or doing the request itself
        :raises: :exc:`UnexpectedAuthError` on unexpected errors while
                 authenticating

        :return: a response from the server contained
                 in the :class:`HttpResponse` object.
        """
        raise NotImplementedError

    def put(self, path: str, body: Dict[str, Any] = None,
            **kwargs) -> HttpResponse:
        """
        Sends a PUT HTTP request.

        :param path: path for the request
        :param body: body of the request
        :param kwargs: Optional arguments that the request takes

        :raises: :exc:`HttpError` on HTTP status codes between 400 and 599
                 while authenticating or doing the request itself
        :raises: :exc:`UnexpectedAuthError` on unexpected errors while
                 authenticating

        :return: a response from the server contained
                 in the :class:`HttpResponse` object.
        """
        raise NotImplementedError

    def delete(self, path: str, **kwargs) -> HttpResponse:
        """
        Sends a DELETE HTTP request.

        :param path: path for the request
        :param kwargs: Optional arguments that the request takes

        :raises: :exc:`HttpError` on HTTP status codes between 400 and 599
                 while authenticating or doing the request itself
        :raises: :exc:`UnexpectedAuthError` on unexpected errors while
                 authenticating

        :return: a response from the server contained
                 in the :class:`HttpResponse` object.
        """
        raise NotImplementedError
