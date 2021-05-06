"""
Module containing the main class of the whole library. This is the class
that users will be interacting with. It's the main entrypoint for all
other actions.
"""
from __future__ import annotations

import sys
import logging
from typing import Optional, Type, Union

import requests

from dsw_sdk.config.config import Config
from dsw_sdk.high_level_api.app_config_api import AppConfigAPI
from dsw_sdk.high_level_api.document_api import DocumentAPI
from dsw_sdk.high_level_api.package_api import PackageAPI
from dsw_sdk.high_level_api.questionnaire_api import QuestionnaireAPI
from dsw_sdk.high_level_api.template_api import TemplateAPI
from dsw_sdk.high_level_api.user_api import UserAPI
from dsw_sdk.http_client.interface import HttpClient
from dsw_sdk.http_client.requests_impl.auth import (
    BodyTokenRetrievalStrategy,
    JWTBearerAuth,
)
from dsw_sdk.http_client.requests_impl.http_client import SessionHttpClient
from dsw_sdk.low_level_api.api import LowLevelAPI


HTTP_CLIENT = Union[HttpClient, Type[HttpClient]]  # pylint: disable=C0103


class DataStewardshipWizardSDK:  # pylint: disable=R0902
    """
    This class provides simple and concise way to communicate with the Data
    Stewardship Wizard API. It offers both low-level and object-oriented
    interfaces.

    Low-level API reflects exactly 1:1 the whole SDK API. For each endpoint
    and each HTTP method there's a function on the low-level interface, which
    is accessible as the :attr:`api` attribute.
    This interface is intended for use cases which are not covered by the
    high-level API, offering 100% of the DSW's functionality.

    High-level object-oriented interface is available for the most common
    operations. It's possible that new features will be added in the future.
    This interface is divided by the entities it is concerned with. Right
    now there are 6 interfaces of this kind, accessible via attributes:

        * :attr:`app_config`
        * :attr:`documents`
        * :attr:`packages`
        * :attr:`questionnaires`
        * :attr:`templates`
        * :attr:`users`

    each containing it's own set of functionality (but in most cases it's
    just CRUD operations).

    There some dependency injection parameters you can pass in order to
    alter the default behavior:

        * ``session`` -- you can pre-configure your own session and pass
          it as the argument; it will be used with the HTTP client
        * ``http_client`` -- either instance or class implementing the
          :class:`~interface.HttpClient` interface. If you pass only
          the class, it will get instantiated with all the other config
          values and auth settings. This way you can override some aspects
          of the default HTTP client, but don't have to initialize it
          yourself. But you can also pass the ready-to-use instance and
          all the HTTP client related config will be ignored.
        * ``logger`` -- if you want, you can specify your own logger.

    All configuration values can be set in 3 different ways:

        * passing as keyword arguments to the :meth:`__init__` method
        * setting values as env variables (prefixed with ``DSW_SDK_``)
        * via config file (in YAML format); path is passed in the
          ``conf_file`` keyword argument

    Here is a list of all possible configuration values:

    .. _config_values:

    :Keyword arguments:
        * **api_url** (`str`):
          URL address of the DSW API you want to connect to. It must contain
          valid url scheme (e.g. `https://`) Mandatory if not passing your
          own ``http_client``.
        * **email** (`str`):
          e-mail address of the user on whose behalf you will be acting.
          Mandatory if not passing your own ``http_client``.
        * **password** (`str`):
          password for logging in. Mandatory if not passing your own
          ``http_client``.
        * **enable_ssl** (`bool`):
          flag defining if the HTTP communication should be encrypted or not.
          Default: ``True``.
        * **auth_endpoint** (`str`):
          endpoint on the DSW API that is responsible for the authorization.
          Default: ``'/tokens'``.
        * **headers** (`Dict[str, str]`):
          Dict of default headers to be sent with every HTTP request.
          Default: ``{}``.
        * **default_timeout**:
          This timeout is used as default value when no timeout is specified
          within a specific request. You can pass one numeric value (applied
          for both the connect and read timeouts), tuple of numeric values to
          specify different connect and read timeouts or ``None`` to wait
          forever. Default: ``(6.05, 27)``:
        * **logger_name** (`str`):
          Name of the default logger. Default: ``'dsw_sdk'``.
        * **logger_level** (`Union[int, str]`):
          Logging level of the default logger. You can use both string levels
          (e.g. ``'INFO'``) or integer levels, ideally constants from the
          :mod:`logging` library (e.g. ``logging.INFO``). Default:
          ``logging.WARNING``.
        * **logger_format** (`str`):
          String describing the format of the default logger. For more info,
          consult the official Python docs about :mod:`logging` module.
          Default: ``[%(asctime)s] - %(name)s | %(levelname)s | %(message)s``.

    Example usage:

    .. code-block:: python

        # Basic configuration
        sdk = DataStewardshipWizardSDK(
            api_url='http://localhost:3000',
            email='albert.einstein@example.com',
            password='password',
        )

        # High-level API usage
        temps = sdk.templates.get_templates(size=2, q='my templates')
        for temp in temps:
            # Each `temp` is a `Template` instance
            print(template.usable_packages[0].version)
            temp.name = 'Modified template name'
            temp.save()
    """

    def __init__(
        self,
        session: requests.Session = None,
        http_client: HTTP_CLIENT = None,
        logger: logging.Logger = None,
        **kwargs,
    ):
        """
        :param session: pre-configured session to be used with the
                        HTTP client instead of the default one
        :param http_client: instance or class implementing the
                            :class:`~interface.HttpClient` interface
        :param logger: pre-configured logger to be used
                       instead of the default one
        """
        self._config = Config(**kwargs)
        self.logger = self._init_logger(logger)
        http_client = self._init_http_client(http_client, session)

        self.api = LowLevelAPI(http_client)
        # High-level object-oriented APIs
        self.app_config = AppConfigAPI(self)
        self.documents = DocumentAPI(self)
        self.packages = PackageAPI(self)
        self.questionnaires = QuestionnaireAPI(self)
        self.templates = TemplateAPI(self)
        self.users = UserAPI(self)

    def _init_logger(self, logger: Optional[logging.Logger]) -> logging.Logger:
        if not logger:
            conf = self._config.logger
            conf.validate()

            logger = logging.Logger(conf.logger_name, conf.logger_level)
            formatter = logging.Formatter(conf.logger_format)
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    def _init_http_client(
        self,
        http_client: Optional[HTTP_CLIENT],
        session: Optional[requests.Session],
    ) -> HttpClient:
        if http_client and not isinstance(http_client, type):
            # If it is an instance of some object, just return it as it has
            # to be already instantiated and configured from the outside
            return http_client

        self._config.http_client.validate()

        auth_url = (f'{self._config.http_client.api_url}'
                    f'{self._config.http_client.auth_endpoint}')
        credentials = {'email': self._config.http_client.email,
                       'password': self._config.http_client.password}

        return (http_client or SessionHttpClient)(  # type: ignore[operator]
            self._config.http_client.api_url,
            JWTBearerAuth(BodyTokenRetrievalStrategy(auth_url, credentials)),
            self.logger,
            session=session,
            **self._config.http_client,
        )
