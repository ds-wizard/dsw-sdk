from dsw_sdk.common.attributes import (
    AttributesMixin,
    BoolAttribute,
    StringAttribute,
)


OWNER_GROUP_MEMBERSHIP = 'OwnerGroupMembershipType'
MEMBER_GROUP_MEMBERSHIP = 'MemberGroupMembershipType'
GROUP_MEMBERSHIP_TYPES = (OWNER_GROUP_MEMBERSHIP, MEMBER_GROUP_MEMBERSHIP)


class UserSuggestion(AttributesMixin):
    first_name = StringAttribute()
    gravatar_hash = StringAttribute()
    image_url = StringAttribute(nullable=True)
    last_name = StringAttribute()
    uuid = StringAttribute()


class UserCreateDTO(AttributesMixin):
    affiliation: str = StringAttribute(nullable=True)  # type: ignore
    email: str = StringAttribute()  # type: ignore
    first_name: str = StringAttribute()  # type: ignore
    last_name: str = StringAttribute()  # type: ignore
    password: str = StringAttribute()  # type: ignore
    role: str = StringAttribute(nullable=True)  # type: ignore


class UserChangeDTO(AttributesMixin):
    active: bool = BoolAttribute()
    affiliation: str = StringAttribute(nullable=True)
    email: str = StringAttribute()
    first_name: str = StringAttribute()
    last_name: str = StringAttribute()
    role: str = StringAttribute()


class GroupMembership(AttributesMixin):
    group_id: str = StringAttribute(immutable=True)
    type: str = StringAttribute(immutable=True, choices=GROUP_MEMBERSHIP_TYPES)
