from typing import Any

from dsw_sdk.common.attributes import AttributesMixin, StringAttribute
from dsw_sdk.common.utils import truncate_long_string
from dsw_sdk.high_level_api.models.model import Model


class TemplateAssetCreateDTO(AttributesMixin):
    content = StringAttribute()
    content_type = StringAttribute(nullable=True)
    file_name = StringAttribute()

    template_id = StringAttribute(immutable=True)

    def files(self):
        file_tuple = (self.file_name, self.content)
        if self.content_type:
            file_tuple += (self.content_type,)
        return {'file': file_tuple}


class TemplateAsset(Model):
    content = StringAttribute()
    content_type = StringAttribute()
    file_name = StringAttribute()

    template_id = StringAttribute(immutable=True)

    def _attr_to_str(self, name: str, value: Any) -> str:
        if name == 'content':
            return truncate_long_string(value, 50)
        return super()._attr_to_str(name, value)

    def _create(self):
        dto = TemplateAssetCreateDTO(**self.attrs())
        data = self._sdk.api.post_template_assets(
            dto.template_id,
            files=dto.files(),
        ).json()
        self._update_attrs(**data)

    def _update(self):
        raise NotImplementedError('You cannot edit a template asset.')

    def _delete(self):
        self._sdk.api.delete_template_asset(self.template_id, self.uuid)
