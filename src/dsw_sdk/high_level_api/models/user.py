from datetime import datetime
from typing import List

from dsw_sdk.common.attributes import (
    BoolAttribute,
    DateTimeAttribute,
    ListAttribute,
    StringAttribute,
)
from dsw_sdk.common.snapshot import make_snapshot, snapshots_diff
from dsw_sdk.common.types import ObjectType, StringType
from dsw_sdk.high_level_api.dto.user import (
    GroupMembership,
    UserChangeDTO,
    UserCreateDTO,
)
from dsw_sdk.high_level_api.models.model import ListOfModelsAttribute, Model
from dsw_sdk.high_level_api.models.questionnaire import Questionnaire


class User(Model):
    _eq_ignore = ['password']

    active: bool = BoolAttribute()
    affiliation: str = StringAttribute(nullable=True)
    created_at: datetime = DateTimeAttribute(nullable=True, read_only=True)
    email: str = StringAttribute()
    first_name: str = StringAttribute()
    groups: List[GroupMembership] = ListAttribute(ObjectType(GroupMembership),
                                                  read_only=True)
    image_url: str = StringAttribute(nullable=True, read_only=True)
    last_name: str = StringAttribute()
    password: str = StringAttribute()
    permissions: List[str] = ListAttribute(StringType(), read_only=True)
    role: str = StringAttribute()
    sources: List[str] = ListAttribute(StringType(), read_only=True)
    updated_at: datetime = DateTimeAttribute(nullable=True, read_only=True)

    questionnaires = ListOfModelsAttribute(Questionnaire, default=[],
                                           read_only=True)

    def _create(self):
        dto = UserCreateDTO(**self.attrs())
        dto.validate()
        data = self._sdk.api.post_users(body=dto.to_json()).json()
        self._update_attrs(**data)

    def _update(self):
        diff = snapshots_diff(self._snapshot, make_snapshot(self))

        if 'password' in diff:
            body = {'password': self.password}
            self._sdk.api.put_user_password(self.uuid, body=body)

        if len(diff) > 1 or 'password' not in diff:
            dto = UserChangeDTO(**self.attrs())
            dto.validate()
            data = self._sdk.api.put_user(self.uuid, body=dto.to_json()).json()
            self._update_attrs(**data)

    def _delete(self):
        self._sdk.api.delete_user(self.uuid)
