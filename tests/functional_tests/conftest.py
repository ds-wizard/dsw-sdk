import random
import string

import pytest
from pytest_data import get_data

from dsw_sdk.high_level_api.dto.questionnaire import (
    PRIVATE_QUESTIONNAIRE,
    RESTRICTED_QUESTIONNAIRE,
)
from dsw_sdk.high_level_api.models.document import (
    Document,
)
from dsw_sdk.high_level_api.models.questionnaire import Questionnaire
from dsw_sdk.high_level_api.models.templates.template import Template
from dsw_sdk.high_level_api.models.templates.template_asset import (
    TemplateAsset,
)
from dsw_sdk.high_level_api.models.templates.template_file import TemplateFile
from dsw_sdk.high_level_api.models.user import User


@pytest.fixture(autouse=True)
def auto_clean(clean):
    """
    Using empty "autouse" fixture to ensure that the `clean` fixture will be
    called automatically for the whole testing module (before each test).
    """
    pass


# ------------------------------- Templates ----------------------------------


def _create_template(dsw_sdk, template_data):
    template_data['allowed_packages'] = [package.to_json() for package in
                                         template_data['allowed_packages']]
    files_data = template_data.pop('files')
    assets_data = template_data.pop('assets')
    # Create template
    template_data = dsw_sdk.api.post_templates(body=template_data).json()
    # Get the template detail to load all the attributes
    template_data.update(dsw_sdk.api.get_template(template_data['id']).json())
    template = Template(dsw_sdk, __update_attrs=template_data)
    # Create template files
    files = []
    for file_data in files_data:
        file = TemplateFile(dsw_sdk, **file_data,
                            template_id=template_data['id'])
        file.save()
        files.append(file)
    template._update_attrs(files=files)
    # Create template assets
    assets = []
    for asset_data in assets_data:
        asset = TemplateAsset(dsw_sdk, **asset_data,
                              template_id=template_data['id'])
        asset.save()
        assets.append(asset)
    template._update_attrs(assets=assets)
    return template


@pytest.fixture
def template(request, dsw_sdk, template_data):
    data = get_data(request, 'template_data', {})
    return _create_template(dsw_sdk, {**template_data, **data})


@pytest.fixture
def templates(request, dsw_sdk, template_data):
    data = get_data(request, 'templates_data', [{}])
    templates = []
    for d in data:
        random_id = ''.join(random.choices(string.ascii_letters, k=10))
        template_data['template_id'] = random_id
        templates.append(_create_template(dsw_sdk, {**template_data, **d}))
    return templates


@pytest.fixture
def registry_template_id(dsw_sdk):
    id_ = 'dsw:science-europe:1.8.0'
    yield id_
    dsw_sdk.templates.delete_templates(ids=[id_])


# ---------------------------- Knowledge models ------------------------------


@pytest.fixture
def registry_package_id(dsw_sdk):
    km_id = 'root'
    id_ = f'dsw:{km_id}:2.3.0'
    yield id_
    dsw_sdk.api.delete_packages(query_params={'kmId': km_id})


# ----------------------------- Questionnaires -------------------------------


def _create_questionnaire(dsw_sdk, package, data=None):
    uuid = dsw_sdk.api.post_questionnaires(body={
        'name': 'test',
        'packageId': package['id'],
        'visibility': PRIVATE_QUESTIONNAIRE,
        'sharing': RESTRICTED_QUESTIONNAIRE,
        'questionTagUuids': [],
        **(data or {}),
    }).json()['uuid']
    questionnaire_data = dsw_sdk.api.get_questionnaire(uuid).json()
    questionnaire_data['package_id'] = package['id']
    return Questionnaire(dsw_sdk, __update_attrs=questionnaire_data)


@pytest.fixture
def questionnaire(dsw_sdk, package):
    return _create_questionnaire(dsw_sdk, package)


@pytest.fixture
def template_questionnaire(dsw_sdk, questionnaire):
    return dsw_sdk.api.put_questionnaire(questionnaire.uuid, body={
        'name': 'test template questionnaire',
        'description': None,
        'isTemplate': True,
        'visibility': PRIVATE_QUESTIONNAIRE,
        'sharing': RESTRICTED_QUESTIONNAIRE,
        'templateId': None,
        'formatUuid': None,
        'permissions': [],
        'projectTags': [],
    }).json()


@pytest.fixture
def questionnaires(request, dsw_sdk, package):
    data = get_data(request, 'questionnaires_data', [{}])
    return [_create_questionnaire(dsw_sdk, package, d) for d in data]


@pytest.fixture
def questionnaire_data(request, package):
    data = {
        'name': 'test questionnaire',
        'package_id': package['id'],
        'sharing': RESTRICTED_QUESTIONNAIRE,
        'visibility': PRIVATE_QUESTIONNAIRE,
        'tag_uuids': [],
        'template_id': None,
        'format_uuid': None,
    }
    return get_data(request, 'questionnaire_data', data)


@pytest.fixture
def questionnaire_template_data(request, template_questionnaire):
    data = {
        'name': 'test questionnaire from template',
        'questionnaire_uuid': template_questionnaire['uuid'],
    }
    return get_data(request, 'questionnaire_template_data', data)


# ------------------------------- Documents ----------------------------------


def _create_document(dsw_sdk, questionnaire, template, data=None):
    document_data = dsw_sdk.api.post_documents(body={
        'name': 'Test document',
        'questionnaire_uuid': questionnaire.uuid,
        'template_id': template.id,
        'format_uuid': 'd3e98eb6-344d-481f-8e37-6a67b6cd1ad2',
        **(data or {}),
    }).json()
    return Document(dsw_sdk, __update_attrs=document_data)


@pytest.fixture
def document(dsw_sdk, questionnaire, template):
    return _create_document(dsw_sdk, questionnaire, template)


@pytest.fixture
def documents(request, dsw_sdk, questionnaire, template):
    data = get_data(request, 'documents_data', [{}])
    return [
        _create_document(dsw_sdk, questionnaire, template, d)
        for d in data
    ]


# ---------------------------------- Users -----------------------------------


def _create_user(dsw_sdk, data):
    user_data = dsw_sdk.api.post_users(body=data).json()
    return User(dsw_sdk, __update_attrs=user_data)


@pytest.fixture
def user(dsw_sdk, user_data):
    return _create_user(dsw_sdk, user_data)


@pytest.fixture
def users(request, dsw_sdk, user_data):
    data = get_data(request, 'users_data', [{}])
    users = []
    for d in data:
        email = ''.join(random.choices(string.ascii_letters, k=10))
        user_data['email'] = f'{email}@example.com'
        users.append(_create_user(dsw_sdk, {**user_data, **d}))
    return users
