from typing import List

from dsw_sdk.high_level_api.api import API, RegistryAPIMixin
from dsw_sdk.high_level_api.models.templates.template import Template
from dsw_sdk.high_level_api.models.templates.template_asset import (
    TemplateAsset,
)
from dsw_sdk.high_level_api.models.templates.template_file import TemplateFile


class TemplatesNotInRegistryError(Exception):
    msg = 'Templates {} were not found in the registry.'

    def __init__(self, ids: List[str]):
        super().__init__(self.msg.format(ids))


class TemplateAPI(API, RegistryAPIMixin):
    model_class = Template

    def _load_files(self, template_id: str) -> List[TemplateFile]:
        files_data = self._sdk.api.get_template_files(template_id).json()
        files = []
        for data in files_data:
            data['template_id'] = template_id
            files.append(TemplateFile(self._sdk, __update_attrs=data))
        return files

    def _load_assets(self, template_id: str) -> List[TemplateAsset]:
        assets_data = self._sdk.api.get_template_assets(template_id).json()
        assets = []
        for data in assets_data:
            asset_content = self._sdk.api.get_template_asset_content(
                template_id,
                data['uuid'],
            ).text
            data['template_id'] = template_id
            data['content'] = asset_content
            assets.append(TemplateAsset(self._sdk, __update_attrs=data))
        return assets

    def get_template(self, id_: str) -> Template:
        template = self._get_one(self._sdk.api.get_template, id_)
        template._update_attrs(files=self._load_files(id_),
                               assets=self._load_assets(id_))
        return template

    def get_templates(
        self,
        organization_id: str = None,
        template_id: str = None,
        **query_params,
    ) -> List[Template]:
        if organization_id is not None:
            query_params['organization_id'] = organization_id
        if template_id is not None:
            query_params['template_id'] = template_id
        templates = self._get_many(self._sdk.api.get_templates,
                                   'templates', **query_params)
        return [self.get_template(template.id) for template in templates]

    def create_template(self, **kwargs) -> Template:
        return self._create_new(**kwargs)

    def delete_template(self, id_: str):
        self._delete_one(self._sdk.api.delete_template, id_)

    def delete_templates(self, organization_id: str = None,
                         ids: List[str] = None):
        if not organization_id and not ids:
            raise ValueError('You must pass either `organization_id` or '
                             'template `ids` in order to delete templates. ')
        if organization_id:
            self._sdk.api.delete_templates(query_params={
                'organization_id': organization_id,
            })
        if ids:
            self._delete_many(self._sdk.api.delete_template, ids)

    def pull_templates(self, ids: List[str]):
        self._pull(self._sdk.api.post_template_pull, 'Templates', ids)

    def update_templates(self, ids: List[str] = None):
        self._update(self.get_template, self.get_templates,
                     self.pull_templates, ids)
