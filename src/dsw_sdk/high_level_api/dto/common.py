from dsw_sdk.common.attributes import (
    AttributesMixin,
    DateTimeAttribute,
    ListAttribute,
    ObjectAttribute,
    StringAttribute,
)
from dsw_sdk.common.types import StringType


OUTDATED_PACKAGE_STATE = 'OutdatedPackageState'
UNKNOWN_PACKAGE_STATE = 'UnknownPackageState'
UNPUBLISHED_PACKAGE_STATE = 'UnpublishedPackageState'
UP_TO_DATE_PACKAGE_STATE = 'UpToDatePackageState'
PACKAGE_STATES = (
    OUTDATED_PACKAGE_STATE,
    UNKNOWN_PACKAGE_STATE,
    UNPUBLISHED_PACKAGE_STATE,
    UP_TO_DATE_PACKAGE_STATE,
)


class OrganizationSimple(AttributesMixin):
    logo = StringAttribute(nullable=True)
    name = StringAttribute()
    organization_id = StringAttribute()


class PackageSimpleDTO(AttributesMixin):
    created_at = DateTimeAttribute()
    description = StringAttribute()
    id = StringAttribute()
    km_id = StringAttribute()
    name = StringAttribute()
    organization = ObjectAttribute(OrganizationSimple, nullable=True)
    organization_id = StringAttribute()
    state = StringAttribute(choices=PACKAGE_STATES)
    version = StringAttribute()
    versions = ListAttribute(StringType())


class PackageSimple(AttributesMixin):
    id = StringAttribute()
    name = StringAttribute()
    version = StringAttribute()
