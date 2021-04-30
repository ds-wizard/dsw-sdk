import logging

from dsw_sdk.http_client.requests_impl.http_client import (
    SessionHttpClient,
)
from dsw_sdk.high_level_api.models.user import User
from high_level_api.models.templates.template import Template
from high_level_api.models.templates.template_file import TemplateFile
from sdk import DataStewardshipWizardSDK


class CustomHttpClient(SessionHttpClient):
    pass


# Every config value should be obtained from (in this order):
#   1. init
#   2. env variables
#   3. config file
dsw_sdk = DataStewardshipWizardSDK(
    # Mandatory if not passing own http client
    api_url='http://localhost:3000',
    email='albert.einstein@example.com',
    password='password',
    # --- Optional arguments for `SessionHttpClient` initialization ---
    # enable_ssl=False,   # E.g. testing purposes, local development
    # auth_endpoint='/tokens',
    # headers={'X-TEST-HEADER': 'TEST HEADER VALUE'},
    # session=requests.Session(),   # Some specific requirements for session (e.g. customize the auth method)
    # default_timeout=(6, 120),   # E.g. for slow networks
    # conf_file='../tests/unit_tests/config/test_config.yaml',
    # --- Logger conf ---
    # logger_level=logging.INFO,
    # logger_name='test logger name',
    # logger_format='%(message)s'
    # --- Dependency injection stuff ---
    # http_client=CustomHttpClient(..., ..., ...),
    # logger=CustomLogger,    # Definitely subclasses of `logging.Logger`
)

# If we don't specify any parameters, we get all templates
templates = dsw_sdk.templates.get_templates()
print(templates)
