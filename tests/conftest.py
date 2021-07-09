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


CASSETTES_DIR = f'{ROOT_DIR}/tests/fixtures/cassettes'


with Betamax.configure() as config:
    config.cassette_library_dir = CASSETTES_DIR


class NoAuthClient(SessionHttpClient):
    pass


def pytest_addoption(parser):
    parser.addoption(
        '--recreate-cassettes',
        action='store_true',
        default=False,
        help='If set, it will create new cassette for each HTTP request. Be '
             'aware that DSW instance must be running on the given address.',
    )
    parser.addoption(
        '--no-cassettes',
        action='store_true',
        default=False,
        help='If set, the Betamax cassettes will not be used and every HTTP '
             'request will be performed as usual.'
    )


@pytest.fixture
def dsw_sdk(request, betamax_session):
    """
    All functional tests and some of the integration tests do actual HTTP
    requests. This fixture operates in 2 modes:

        1) If you pass a `--recreate-cassettes` option to the pytest command
        when running the tests, it will connect to the DSW API, do every HTTP
        request and record it's response to a Betamax cassette.
        Make sure that the cassettes folder is empty!

        2) If no option is passed, the SDK won't do any HTTP request at all.
        Instead, it will read the responses from the cassettes. If there is no
        matching cassette for a given request, the test will fail.
    """
    recreate_cassettes = request.config.option.recreate_cassettes
    no_cassettes = request.config.option.no_cassettes
    if recreate_cassettes and no_cassettes:
        raise ValueError('Cannot use both options `--recreate-cassettes` '
                         'and --no-cassettes as the same time.')

    if recreate_cassettes:
        return DataStewardshipWizardSDK(
            api_url='http://localhost:3000',
            email='albert.einstein@example.com',
            password='password',
            session=betamax_session,
        )
    elif no_cassettes:
        return DataStewardshipWizardSDK(
            api_url='http://localhost:3000',
            email='albert.einstein@example.com',
            password='password',
        )
    else:
        # If we are using cassettes (and thus not doing any HTTP requests),
        # we must suppress the authentication as it doesn't use a session.
        client = NoAuthClient('http://localhost:3000', None,
                              logging.root, session=betamax_session)
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
        'organization_id': 'Test_org',
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
