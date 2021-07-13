"""
Templates high-level API.
"""
from __future__ import annotations

from typing import List

from dsw_sdk.high_level_api.common_api import API, RegistryAPIMixin
from dsw_sdk.high_level_api.models.templates.template import Template
from dsw_sdk.high_level_api.models.templates.template_asset import (
    TemplateAsset,
)
from dsw_sdk.high_level_api.models.templates.template_file import TemplateFile


class TemplateAPI(API, RegistryAPIMixin):
    """
    API for the Template entities.

    Supports all of the CRUD operations and pulling/updating templates.

    Example usage:

    .. code-block:: python

        api = TemplateAPI(...)

        # Get one template by ID
        template = api.get_template('dsw:template:1.0.0')

        # Get all templates for a given organization
        templates = api.get_templates(organization_id='dsw')

        # Get page number 1 (each page having 10 templates) of templates
        # containing the "foo" string, sorted by the UUID attribute in the
        # ascending order
        templates = api.get_templates(q='foo', page=1, size=10, start='id,asc')

        # Create template
        template = api.create_template(template_id='new_temp', ...)

        # Delete template
        api.delete_template(template.id)

        # Delete all templates for a given organization
        api.delete_templates(organization_id='dsw')

        # Delete list of templates
        api.delete_templates(ids=['dsw:template:1.0.0', 'dsw:temp:2.3.1'])

        # Pull specified templates from the Data Stewardship Registry
        api.pull_templates(['dsw:template:1.0.0', 'dsw:temp:2.3.1'])

        # Update specified templates (so that they have latest version
        # available)
        api.update_templates(['dsw:template:1.0.0', 'dsw:temp:2.3.1'])

        # Update all templates to the latest version available
        api.update_templates()
    """
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
        """
        Retrieves one template, identified by it's ID.
        Also loading all of it's related files and assets.

        :param id_: template identifier

        :return: object representing a template
        """
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
        """
        Retrieves list of templates.
        Also loading all related files and assets.

        Possibly identified by the organization to which they belong to. It's
        also possible to search based on the ``template_id`` (note that this
        is different from template's ``id`` attribute).

        :param organization_id: ID of the organization whose templates we
            want to fetch
        :param template_id: ``template_id`` attribute of a template
            (different from ``id`` attribute)
        :param query_params: optional query params: ``q``, ``size``, ``page``
            and ``sort``

        :return: list of objects, each representing a template
        """
        if organization_id is not None:
            query_params['organization_id'] = organization_id
        if template_id is not None:
            query_params['template_id'] = template_id
        templates = self._get_many_data(self._sdk.api.get_templates,
                                        'templates', **query_params)
        return [self.get_template(template['id']) for template in templates]

    def create_template(self, **kwargs) -> Template:
        """
        Creates a template with given data on the DSW server.

        :param kwargs: all the data needed for the template creation

        :return: object representing the new template
        """
        return self._create_new(**kwargs)

    def delete_template(self, id_: str):
        """
        Deletes a template from the DSW server.

        :param `id_`: ID of the template to delete
        """
        self._delete_one(self._sdk.api.delete_template, id_)

    def delete_templates(self, organization_id: str = None,
                         ids: List[str] = None):
        """
        Deletes multiple templates on the DSW server, identified either by
        organization or ID.

        :param organization_id: ID of the organization whose templates we
            want to delete
        :param ids: IDs of templates to delete
        """
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
        """
        Pulls given templates from the Data Stewardship Registry, so they
        become available in the DSW instance.

        :param ids: IDs of the templates you want to pull form the registry
        """
        self._pull(self._sdk.api.post_template_pull, 'Templates', ids)

    def update_templates(self, ids: List[str] = None):
        """
        Updates specified templates, pulling their latest available version.
        If no IDs are given, updates *all* templates on the DSW instance.

        :param ids: optional list of template IDs to update
        """
        self._update(self.get_template, self.get_templates,
                     self.pull_templates, ids)
