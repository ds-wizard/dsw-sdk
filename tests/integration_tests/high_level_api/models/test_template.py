import pytest

from dsw_sdk.common.attributes import AttributeNotSetError
from dsw_sdk.high_level_api.dto.template import TemplateFormat
from dsw_sdk.high_level_api.models.templates.template import Template
from dsw_sdk.high_level_api.models.templates.template_asset import (
    TemplateAsset,
)
from dsw_sdk.high_level_api.models.templates.template_file import TemplateFile


def test_create_template(betamax_dsw_sdk, template_data):
    template = Template(betamax_dsw_sdk, **template_data)
    template.save()

    assert template.uuid is not None
    assert isinstance(template.formats[0], TemplateFormat)


def test_create_template_missing_attr(template_data):
    del template_data['description']
    template = Template(..., **template_data)
    with pytest.raises(AttributeNotSetError) as e:
        template.save()
    assert e.match(e.value.msg.format('description'))


def test_create_template_with_files(betamax_dsw_sdk, template_data):
    template = Template(betamax_dsw_sdk, **template_data)
    # When assigning to the list attribute, we can
    # pass dict representation of the object.
    template.files = [{
        'content': '<html>Some content</html>',
        'file_name': 'some_filename.html',
    }]
    # While extending an existing list, we must pass the actual object
    template.files.append(
        TemplateFile(betamax_dsw_sdk, content='123', file_name='foo.txt'),
    )

    template.save()
    assert len(template.files) == 2
    for file in template.files:
        assert isinstance(file, TemplateFile)
        assert file.uuid is not None


def test_create_template_with_files_with_id():
    template = Template(..., files=[{
        'content': '<html>Some content</html>',
        'file_name': 'some_filename.html',
        'template_id': 'some_template_id'
    }])
    with pytest.raises(ValueError):
        template.save()


def test_update_template_with_files_with_id():
    template = Template(..., __update_attrs={'files': [{
        'content': '<html>Some content</html>',
        'file_name': 'some_filename.html',
        'template_id': 'some_template_id'
    }]})
    template.name = 'some change'
    with pytest.raises(ValueError):
        template.save()


def test_create_template_with_assets(betamax_dsw_sdk, template_data):
    template = Template(betamax_dsw_sdk, **template_data)
    # When assigning to the list attribute, we can
    # pass dict representation of the object.
    template.assets = [{
        'content': '<html>Some content</html>',
        'contentType': 'text/html',
        'file_name': 'some_filename.html',
    }]
    # While extending an existing list, we must pass the actual object
    template.assets.append(
        TemplateAsset(
            betamax_dsw_sdk,
            content='123',
            content_type='text/plain',
            file_name='foo.txt',
        ),
    )

    template.save()
    assert len(template.assets) == 2
    for asset in template.assets:
        assert isinstance(asset, TemplateAsset)
        assert asset.uuid is not None


def test_create_template_with_assets_with_id():
    template = Template(..., assets=[{
        'content': '<html>Some content</html>',
        'content_type': 'text/html',
        'file_name': 'some_filename.html',
        'template_id': 'some_template_id'
    }])
    with pytest.raises(ValueError):
        template.save()


def test_update_template_with_assets_with_id():
    template = Template(..., __update_attrs={'assets': [{
        'content': '<html>Some content</html>',
        'content_type': 'text/html',
        'file_name': 'some_filename.html',
        'template_id': 'some_template_id'
    }]})
    template.name = 'some change'
    with pytest.raises(ValueError):
        template.save()
