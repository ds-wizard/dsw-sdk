from dsw_sdk.common.attributes import (
    AttributesMixin,
    DateTimeAttribute,
    DictAttribute,
    IntegerAttribute,
    ListAttribute,
    ObjectAttribute,
    StringAttribute,
)
from dsw_sdk.common.types import ObjectType, StringType
from dsw_sdk.high_level_api.dto.common import (
    OrganizationSimple,
    PackageSimpleDTO,
)


OUTDATED_TEMPLATE_STATE = 'OutdatedTemplateState'
UNKNOWN_TEMPLATE_STATE = 'UnknownTemplateState'
UNPUBLISHED_TEMPLATE_STATE = 'UnpublishedTemplateState'
UP_TO_DATE_TEMPLATE_STATE = 'UpToDateTemplateState'
UNSUPPORTED_METAMODEL_VERSION_TEMPLATE_STATE = ('UnsupportedMetamodel'
                                                'VersionTemplateState')
TEMPLATE_STATES = (
    OUTDATED_TEMPLATE_STATE,
    UNKNOWN_TEMPLATE_STATE,
    UNPUBLISHED_TEMPLATE_STATE,
    UNSUPPORTED_METAMODEL_VERSION_TEMPLATE_STATE,
    UP_TO_DATE_TEMPLATE_STATE,
)


class TemplateAllowedPackage(AttributesMixin):
    km_id = StringAttribute(nullable=True)
    max_version = StringAttribute(nullable=True)
    min_version = StringAttribute(nullable=True)
    org_id = StringAttribute(nullable=True)


class TemplateFormatStep(AttributesMixin):
    name = StringAttribute()
    options = DictAttribute(StringType(), StringType())


class TemplateFormat(AttributesMixin):
    color = StringAttribute()
    icon = StringAttribute()
    name = StringAttribute()
    short_name = StringAttribute()
    steps = ListAttribute(ObjectType(TemplateFormatStep), nullable=True)
    uuid = StringAttribute()


class TemplateChangeDTO(AttributesMixin):
    allowed_packages = ListAttribute(ObjectType(TemplateAllowedPackage))
    description = StringAttribute()
    formats = ListAttribute(ObjectType(TemplateFormat))
    license = StringAttribute()
    metamodel_version = IntegerAttribute()
    name = StringAttribute()
    organization_id = StringAttribute()
    readme = StringAttribute()
    recommended_package_id = StringAttribute(nullable=True)
    template_id = StringAttribute()
    version = StringAttribute()


class TemplateSimple(AttributesMixin):
    description = StringAttribute()
    formats = ListAttribute(ObjectType(TemplateFormat))
    id = StringAttribute()
    name = StringAttribute()
    version = StringAttribute()


class TemplateSimpleDTO(TemplateSimple):
    allowed_packages = ListAttribute(ObjectType(TemplateAllowedPackage))
    created_at = DateTimeAttribute(read_only=True)
    license = StringAttribute()
    metamodel_version = IntegerAttribute()
    organization = ObjectAttribute(OrganizationSimple, nullable=True,
                                   read_only=True)
    organization_id = StringAttribute()
    readme = StringAttribute()
    recommended_package_id = StringAttribute(nullable=True)
    state = StringAttribute(choices=TEMPLATE_STATES, read_only=True)
    template_id = StringAttribute()
    usable_packages = ListAttribute(ObjectType(PackageSimpleDTO),
                                    read_only=True)
