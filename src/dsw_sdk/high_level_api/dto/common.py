from dsw_sdk.common.attributes import (
    AttributesMixin,
    DateTimeAttribute,
    ListAttribute,
    ObjectAttribute,
    StringAttribute,
)
from dsw_sdk.common.types import StringType
from dsw_sdk.high_level_api.dto.user import UserSuggestion


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

DONE_SUBMISSION_STATE = 'DoneSubmissionState'
ERROR_SUBMISSION_STATE = 'ErrorSubmissionState'
IN_PROGRESS_SUBMISSION_STATE = 'InProgressSubmissionState'
SUBMISSION_STATES = (
    DONE_SUBMISSION_STATE,
    ERROR_SUBMISSION_STATE,
    IN_PROGRESS_SUBMISSION_STATE,
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
    remote_latest_version = StringAttribute(nullable=True)
    state = StringAttribute(choices=PACKAGE_STATES)
    version = StringAttribute()
    versions = ListAttribute(StringType())


class PackageSimple(AttributesMixin):
    id = StringAttribute()
    name = StringAttribute()
    version = StringAttribute()


class SubmissionDTO(AttributesMixin):
    created_at = DateTimeAttribute()
    created_by = ObjectAttribute(UserSuggestion)
    document_uuid = StringAttribute()
    location = StringAttribute(nullable=True)
    returned_data = StringAttribute()
    service_id = StringAttribute()
    service_name = StringAttribute(nullable=True)
    state = StringAttribute(choices=SUBMISSION_STATES)
    updated_at = DateTimeAttribute()
    uuid = StringAttribute()
