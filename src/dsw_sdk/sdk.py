"""
TBD
"""
import sys
from logging import Formatter, Logger, StreamHandler
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


HTTP_CLIENT = Union[HttpClient, Type[HttpClient]]


class DataStewardshipWizardSDK:
    """
    TBD
    """

    def __init__(
        self,
        session: requests.Session = None,
        http_client: HTTP_CLIENT = None,
        logger: Logger = None,
        **kwargs,
    ):
        """
        TBD

        :param api_url:
        :param http_client:
        :param logger:
        """
        self._config = Config(**kwargs)
        self.logger = self._init_logger(logger)
        http_client = self._init_http_client(http_client, session)

        self.api = LowLevelAPI(http_client)
        self.app_config = AppConfigAPI(self)
        self.documents = DocumentAPI(self)
        self.packages = PackageAPI(self)
        self.questionnaires = QuestionnaireAPI(self)
        self.templates = TemplateAPI(self)
        self.users = UserAPI(self)

    def _init_logger(self, logger: Optional[Logger]) -> Logger:
        if not logger:
            conf = self._config.logger
            conf.validate()

            logger = Logger(conf.logger_name, conf.logger_level)
            formatter = Formatter(conf.logger_format)
            handler = StreamHandler(sys.stdout)
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

        return (http_client or SessionHttpClient)(
            self._config.http_client.api_url,
            JWTBearerAuth(BodyTokenRetrievalStrategy(auth_url, credentials)),
            self.logger,
            session=session,
            **self._config.http_client,
        )
