# pylint: disable=E1133

from datetime import datetime
from typing import Any, List, Optional

from dsw_sdk.common.attributes import (
    Alias,
    DateTimeAttribute,
    IntegerAttribute,
    ListAttribute,
    ObjectAttribute,
    StringAttribute,
)
from dsw_sdk.common.snapshot import SnapshotDiff, make_snapshot, snapshots_diff
from dsw_sdk.common.types import ObjectType, StringType
from dsw_sdk.common.utils import truncate_long_string
from dsw_sdk.high_level_api.dto.common import (
    OrganizationSimple,
    PackageSimpleDTO,
)
from dsw_sdk.high_level_api.dto.template import (
    TEMPLATE_STATES,
    TemplateAllowedPackage,
    TemplateChangeDTO, TemplateFormat,
)
from dsw_sdk.high_level_api.models.model import (
    ListOfModelsAttribute,
    Model,
)
from dsw_sdk.high_level_api.models.templates.template_asset import (
    TemplateAsset,
)
from dsw_sdk.high_level_api.models.templates.template_file import TemplateFile


CREATE_VALIDATE_ERR = ('Invalid `{}` attribute: `template_id` of a {} '
                       'cannot be set when creating new template')
UPDATE_VALIDATE_ERR = ('Invalid `{}` attribute: `template_id` of a {} must be '
                       'same as `uuid` attribute of corresponding template')


class Template(Model):
    allowed_packages: List[TemplateAllowedPackage] = ListAttribute(
        ObjectType(TemplateAllowedPackage),
    )
    created_at: datetime = DateTimeAttribute(read_only=True)
    description: str = StringAttribute()
    formats: List[TemplateFormat] = ListAttribute(ObjectType(TemplateFormat))
    id: str = Alias('uuid')
    license: str = StringAttribute()
    metamodel_version: int = IntegerAttribute()
    name: str = StringAttribute()
    organization: Optional[OrganizationSimple] = ObjectAttribute(
        OrganizationSimple,
        nullable=True,
        read_only=True,
    )
    organization_id: str = StringAttribute()
    readme: str = StringAttribute()
    recommended_package_id: Optional[str] = StringAttribute(nullable=True)
    registry_link: Optional[str] = StringAttribute(
        nullable=True,
        read_only=True,
    )
    remote_latest_version: Optional[str] = StringAttribute(
        nullable=True,
        read_only=True,
    )
    state: str = StringAttribute(choices=TEMPLATE_STATES, read_only=True)
    template_id: str = StringAttribute()
    usable_packages: List[PackageSimpleDTO] = ListAttribute(
        ObjectType(PackageSimpleDTO),
        read_only=True,
    )
    version: str = StringAttribute()
    versions: List[str] = ListAttribute(StringType(), read_only=True)

    assets: List[TemplateAsset] = ListOfModelsAttribute(TemplateAsset,
                                                        default=[])
    files: List[TemplateFile] = ListOfModelsAttribute(TemplateFile,
                                                      default=[])

    def _attr_to_str(self, name: str, value: Any) -> str:
        # Readme is usually quite long, so we display only the beginning
        if name == 'readme':
            return truncate_long_string(value, 50)
        return super()._attr_to_str(name, value)

    def _create_validate(self):
        for file in self.files:
            if file.template_id is not None:
                raise ValueError(CREATE_VALIDATE_ERR.format('files', 'file'))
        for asset in self.assets:
            if asset.template_id is not None:
                raise ValueError(CREATE_VALIDATE_ERR.format('assets', 'asset'))

    def _update_validate(self):
        for file in self.files:
            if (
                file.template_id is not None
                and file.template_id != self.uuid
            ):
                raise ValueError(UPDATE_VALIDATE_ERR.format('files', 'file'))
        for asset in self.assets:
            if (
                asset.template_id is not None
                and asset.template_id != self.uuid
            ):
                raise ValueError(UPDATE_VALIDATE_ERR.format('assets', 'asset'))

    def _save_template_files(self, diff: SnapshotDiff = SnapshotDiff()):
        modified_files_uuids = [file['uuid'] for file in
                                diff.modified.get('files', [])]
        for file in self.files:
            if file.uuid in modified_files_uuids:
                modified_files_uuids.remove(file.uuid)
            file.template_id = self.uuid
            # If it is a new file, it gets created. If it is some old file,
            # that was just modified, it gets updated. If no there was no
            # change, `file.save()` won't do anything.
            file.save()

        for uuid_to_remove in modified_files_uuids:
            self._sdk.api.delete_template_file(self.uuid, uuid_to_remove)

    def _save_asset_files(self, diff: SnapshotDiff = SnapshotDiff()):
        modified_assets_uuids = [asset['uuid'] for asset in
                                 diff.modified.get('assets', [])]

        for asset in self.assets:
            if asset.uuid in modified_assets_uuids:
                modified_assets_uuids.remove(asset.uuid)
            asset.template_id = self.uuid
            asset.save()

        for uuid_to_remove in modified_assets_uuids:
            self._sdk.api.delete_template_asset(self.uuid, uuid_to_remove)

    def _create(self):
        self._create_validate()
        dto = TemplateChangeDTO(**self.attrs())
        dto.validate()
        data = self._sdk.api.post_templates(body=dto.to_json()).json()
        # We must pop the `files` and `assets`, because they are not yet
        # created on the server, so there are only empty lists in `data`.
        data.pop('files', None)
        data.pop('assets', None)
        self._update_attrs(**data)
        self._save_template_files()
        self._save_asset_files()

        data = self._sdk.api.get_template(self.id).json()
        self._update_attrs(**data)

    def _update(self):
        self._update_validate()
        diff = snapshots_diff(self._snapshot, make_snapshot(self))

        if 'files' in diff:
            self._save_template_files(diff)
        if 'assets' in diff:
            self._save_asset_files(diff)
        if len(diff) > 2 or ('files' not in diff and 'assets' not in diff):
            dto = TemplateChangeDTO(**self.attrs())
            dto.validate()
            data = self._sdk.api.put_template(
                self.uuid,
                body=dto.to_json(),
            ).json()
            self._update_attrs(**data)

    def _delete(self):
        self._sdk.api.delete_template(self.uuid)
