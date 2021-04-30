import logging
import os
import random
import string

import pytest
from betamax import Betamax
from pytest_data import get_data

from dsw_sdk import DataStewardshipWizardSDK
from dsw_sdk.high_level_api.dto.template import TemplateAllowedPackage
from dsw_sdk.http_client.requests_impl.http_client import SessionHttpClient


ROOT_DIR = os.path.abspath(
    os.path.join(
        __file__,
        os.path.pardir,
        os.path.pardir,
    )
)


with Betamax.configure() as config:
    config.cassette_library_dir = f'{ROOT_DIR}/tests/fixtures/cassettes'


@pytest.fixture(scope='module')
def dsw_sdk():
    return DataStewardshipWizardSDK(
        api_url='http://localhost:3000',
        email='albert.einstein@example.com',
        password='password',
    )


class NoAuthClient(SessionHttpClient):
    pass


@pytest.fixture
def betamax_dsw_sdk(betamax_session):
    """
    This is intended to fail if it tries to connect to the DSW API. If you
    need to generate new cassettes, initialize SDK same as in `dsw_sdk`
    fixture, with Betamax session.
    """
    client = NoAuthClient(
        'http://localhost:3000',
        None,
        logging.root,
        session=betamax_session,
    )
    return DataStewardshipWizardSDK(http_client=client)


# ---------------------------------- Users -----------------------------------


@pytest.fixture
def user_data(request):
    email = ''.join(random.choices(string.ascii_letters, k=10))
    data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': f'{email}@example.com',
        'password': 'password',
        'affiliation': 'My university',
        'role': 'researcher',
    }
    return get_data(request, 'user_data_data', data)


# -------------------------------- Templates ---------------------------------


@pytest.fixture
def template_data():
    # Testing creating templates with both object ('allowed_packages')
    # and Python dict ('formats').
    return {
        'allowed_packages': [
            TemplateAllowedPackage(
                min_version=None,
                km_id=None,
                max_version=None,
                org_id='global',
            ),
        ],
        'description': 'Description',
        'formats': [{
            'short_name': 'json',
            'color': 'blue',
            'uuid': 'd3e98eb6-344d-481f-8e37-6a67b6cd1ad2',
            'icon': 'icon',
            'steps': [{
                'name': 'json',
                'options': {}
            }],
            'name': 'JSON Data'
        }],
        'license': 'MIT',
        'metamodel_version': 3,
        'name': 'Test template',
        'organization_id': 'Test org',
        'readme': 'dont read me',
        'template_id': ''.join(random.choices(string.ascii_letters, k=10)),
        'version': '1.2.0',
        'files': [{
            'content': '<html>Some content</html>',
            'file_name': 'some_file.html',
        }],
        'assets': [{
            'content': '123',
            'content_type': 'text/plain',
            'file_name': 'foo.txt',
        }],
    }
