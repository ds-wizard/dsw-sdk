from datetime import datetime

import pytest
from pytest_data import use_data

from dsw_sdk.high_level_api.models.templates.template import (
    TEMPLATE_STATES, Template, TemplateAllowedPackage, TemplateFormat,
)
from dsw_sdk.high_level_api.models.templates.template_asset import (
    TemplateAsset,
)
from dsw_sdk.high_level_api.models.templates.template_file import TemplateFile
from dsw_sdk.http_client.interface import NotFoundError


def _template_check(template):
    assert template.id is not None
    assert template.uuid is not None
    assert template.uuid is template.id
    assert isinstance(template.created_at, datetime)
    assert isinstance(template.allowed_packages, list)
    assert isinstance(template.allowed_packages[0], TemplateAllowedPackage)
    assert isinstance(template.formats, list)
    assert isinstance(template.formats[0], TemplateFormat)
    # Check that the `state` attribute is present (and
    # therefore we have the complete Template object)
    assert template.state in TEMPLATE_STATES
    # Check that files are correctly created
    assert isinstance(template.files, list)
    assert len(template.files) == 1
    assert isinstance(template.files[0], TemplateFile)
    assert template.files[0].uuid is not None
    # Check that assets are correctly created
    assert isinstance(template.assets, list)
    assert len(template.assets) == 1
    assert isinstance(template.assets[0], TemplateAsset)
    assert template.assets[0].uuid is not None
    # Check that asset's content is loaded
    assert template.assets[0].content is not None


def test_create_template_via_api(dsw_sdk, template_data):
    template = dsw_sdk.templates.create_template(**template_data)
    _template_check(template)


def test_create_template_via_object(dsw_sdk, template_data):
    template = Template(dsw_sdk, **template_data)
    template.save()
    _template_check(template)


def test_get_one_template(dsw_sdk, template):
    loaded_template = dsw_sdk.templates.get_template(template.id)
    assert loaded_template == template
    _template_check(loaded_template)


@use_data(templates_data=[
    {'organization_id': 'foo'},
    {'organization_id': 'foo'},
    {'organization_id': 'foo'},
])
def test_get_many_templates(dsw_sdk, templates):
    res = dsw_sdk.templates.get_templates()
    assert len(res) >= 3

    res = dsw_sdk.templates.get_templates(template_id=templates[0].template_id)
    assert len(res) == 1
    assert res[0] == templates[0]
    _template_check(res[0])

    # Works only with `template_id`, not the `id`
    res = dsw_sdk.templates.get_templates(template_id=templates[0].id)
    assert len(res) == 0

    org_id = templates[0].organization_id
    res = dsw_sdk.templates.get_templates(organization_id=org_id)
    assert len(res) == 3
    for template in templates:
        assert template in res


def test_update_template(dsw_sdk, template):
    template.license = 'New license'
    template.allowed_packages = [
        TemplateAllowedPackage(org_id='dsw'),
    ]
    template_file = TemplateFile(dsw_sdk, content='some text',
                                 file_name='text/plain')
    template.files.append(template_file)
    template.assets.pop(0)
    template.save()

    # Load the template from scratch to ensure that
    # the changes took place on the server
    template = dsw_sdk.templates.get_template(template.id)
    assert template.license == 'New license'
    assert template.allowed_packages == [TemplateAllowedPackage(org_id='dsw')]
    assert template.assets == []

    assert len(template.files) == 2
    assert template.files[1] == template_file


def test_delete_one_template(dsw_sdk, template):
    dsw_sdk.templates.delete_template(template.id)
    with pytest.raises(NotFoundError):
        dsw_sdk.templates.get_template(template.id)


@use_data(templates_data=[{}, {}, {}])
def test_delete_many_templates(dsw_sdk, templates):
    dsw_sdk.templates.delete_templates(ids=[t.id for t in templates])
    for template in templates:
        with pytest.raises(NotFoundError):
            dsw_sdk.templates.get_template(template.id)


@use_data(templates_data=[{}, {}, {}])
def test_delete_many_templates_via_organization_id(dsw_sdk, templates):
    org_id = templates[0].organization_id
    dsw_sdk.templates.delete_templates(organization_id=org_id)
    for template in templates:
        with pytest.raises(NotFoundError):
            dsw_sdk.templates.get_template(template.id)


@pytest.mark.parametrize('bulk_update', [True, False])
@use_data(template_data={
    'organization_id': 'dsw',
    'template_id': 'science-europe',
    'version': '1.4.1',
})
def test_update_templates(
    dsw_sdk,
    template,
    registry_template_id,
    bulk_update,
):
    registry_outdated_template_id = 'dsw:science-europe:1.4.1'
    # Make sure that we have the outdated template from the registry
    dsw_sdk.templates.pull_templates([registry_outdated_template_id])
    dsw_sdk.templates.get_template(registry_outdated_template_id)
    # And that we don't have the latest version
    with pytest.raises(NotFoundError):
        dsw_sdk.templates.get_template(registry_template_id)

    if bulk_update:
        dsw_sdk.templates.update_templates()
    else:
        dsw_sdk.templates.update_templates([registry_outdated_template_id])
    # Now we have the latest version
    dsw_sdk.templates.get_template(registry_template_id)


def test_pull_templates(dsw_sdk, registry_template_id):
    with pytest.raises(NotFoundError):
        dsw_sdk.templates.get_template(registry_template_id)

    dsw_sdk.templates.pull_templates([registry_template_id])
    dsw_sdk.templates.get_template(registry_template_id)
