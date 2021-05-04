from typing import Any

from dsw_sdk.common.attributes import AttributesMixin, StringAttribute
from dsw_sdk.common.utils import truncate_long_string
from dsw_sdk.high_level_api.models.model import Model


class TemplateFileChangeDTO(AttributesMixin):
    content = StringAttribute()
    file_name = StringAttribute()

    template_id = StringAttribute(immutable=True)


class TemplateFile(Model):
    content = StringAttribute()
    file_name = StringAttribute()

    template_id = StringAttribute(immutable=True)

    def _attr_to_str(self, name: str, value: Any) -> str:
        if name == 'content':
            return truncate_long_string(value, 50)
        return super()._attr_to_str(name, value)

    def _create(self):
        dto = TemplateFileChangeDTO(**self.attrs())
        data = self._sdk.api.post_template_files(
            dto.template_id,
            body=dto.to_json(),
        ).json()
        self._update_attrs(**data)

    def _update(self):
        dto = TemplateFileChangeDTO(**self.attrs())
        data = self._sdk.api.put_template_file(
            dto.template_id,
            self.uuid,
            body=dto.to_json(),
        ).json()
        self._update_attrs(**data)

    def _delete(self):
        self._sdk.api.delete_template_file(self.template_id, self.uuid)
