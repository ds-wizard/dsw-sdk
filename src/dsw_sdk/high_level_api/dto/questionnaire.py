from dsw_sdk.common.attributes import (
    Attribute,
    AttributesMixin,
    DateTimeAttribute,
    IntegerAttribute,
    ListAttribute,
    ObjectAttribute,
    StringAttribute,
)
from dsw_sdk.common.types import MappingType, ObjectType, StringType
from dsw_sdk.high_level_api.dto.user import UserSuggestion


PRIVATE_QUESTIONNAIRE = 'PrivateQuestionnaire'
VISIBLE_EDIT_QUESTIONNAIRE = 'VisibleEditQuestionnaire'
VISIBLE_VIEW_QUESTIONNAIRE = 'VisibleViewQuestionnaire'
QUESTIONNAIRE_VISIBILITIES = (
    PRIVATE_QUESTIONNAIRE,
    VISIBLE_EDIT_QUESTIONNAIRE,
    VISIBLE_VIEW_QUESTIONNAIRE,
)

ANYONE_WITH_LINK_EDIT_QUESTIONNAIRE = 'AnyoneWithLinkEditQuestionnaire'
ANYONE_WITH_LINK_VIEW_QUESTIONNAIRE = 'AnyoneWithLinkViewQuestionnaire'
RESTRICTED_QUESTIONNAIRE = 'RestrictedQuestionnaire'
QUESTIONNAIRE_SHARING = (
    ANYONE_WITH_LINK_EDIT_QUESTIONNAIRE,
    ANYONE_WITH_LINK_VIEW_QUESTIONNAIRE,
    RESTRICTED_QUESTIONNAIRE,
)

DEFAULT_STATE = 'Default'
MIGRATING_STATE = 'Migrating'
OUTDATED_STATE = 'Outdated'
QUESTIONNAIRE_STATES = (
    DEFAULT_STATE,
    MIGRATING_STATE,
    OUTDATED_STATE,
)

ANSWER_REPLY = 'AnswerReply'
INTEGRATION_REPLY = 'IntegrationReply'
ITEM_LIST_REPLY = 'ItemListReply'
MULTI_CHOICE_REPLY = 'MultiChoiceReply'
STRING_REPLY = 'StringReply'
QUESTIONNAIRE_REPLIES = (
    ANSWER_REPLY,
    INTEGRATION_REPLY,
    ITEM_LIST_REPLY,
    MULTI_CHOICE_REPLY,
    STRING_REPLY,
)

GROUP_MEMBER = 'GroupMember'
USER_MEMBER = 'UserMember'
MEMBER_TYPES = (GROUP_MEMBER, USER_MEMBER)

CLEAR_REPLY_EVENT = 'ClearReplyEvent'
SET_LABELS_EVENT = 'SetLabelsEvent'
SET_PHASE_EVENT = 'SetPhaseEvent'
SET_REPLY_EVENT = 'SetReplyEvent'
EVENT_TYPES = (
    CLEAR_REPLY_EVENT,
    SET_LABELS_EVENT,
    SET_PHASE_EVENT,
    SET_REPLY_EVENT,
)

ANSWERED_INDICATION = 'AnsweredIndication'
PHASES_ANSWERED_INDICATION = 'PhasesAnsweredIndication'
INDICATIONS_TYPES = (ANSWERED_INDICATION, PHASES_ANSWERED_INDICATION)

INTEGRATION_TYPE = 'IntegrationType'
PLAIN_TYPE = 'PlainType'
INTEGRATION_REPLY_TYPES = (INTEGRATION_TYPE, PLAIN_TYPE)


class IntegrationReplyType(AttributesMixin):
    value = StringAttribute()
    type = StringAttribute(choices=INTEGRATION_REPLY_TYPES)


class PlainType(IntegrationReplyType):
    pass


class IntegrationType(IntegrationReplyType):
    id = StringAttribute()


class ReplyValue(AttributesMixin):
    type = StringAttribute(choices=QUESTIONNAIRE_REPLIES)


class StringReply(ReplyValue):
    value = StringAttribute()


class AnswerReply(ReplyValue):
    value = StringAttribute()


class MultiChoiceReply(ReplyValue):
    value = ListAttribute(StringType())


class ItemListReply(ReplyValue):
    value = ListAttribute(StringType())


class IntegrationReply(ReplyValue):
    value = Attribute(MappingType('type', {
        PLAIN_TYPE: ObjectType(PlainType),
        INTEGRATION_TYPE: ObjectType(IntegrationType),
    }))


class Reply(AttributesMixin):
    created_at = DateTimeAttribute()
    created_by = ObjectAttribute(UserSuggestion)
    value = Attribute(MappingType('type', {
        ANSWER_REPLY: ObjectType(AnswerReply),
        INTEGRATION_REPLY: ObjectType(IntegrationReply),
        ITEM_LIST_REPLY: ObjectType(ItemListReply),
        MULTI_CHOICE_REPLY: ObjectType(MultiChoiceReply),
        STRING_REPLY: ObjectType(StringReply),
    }))


class GroupMember(AttributesMixin):
    gid = StringAttribute()
    name = StringAttribute()
    type = StringAttribute(choices=MEMBER_TYPES)


class UserMember(UserSuggestion):
    type = StringAttribute(choices=MEMBER_TYPES)


class QuestionnairePermRecordDTO(AttributesMixin):
    member = Attribute(MappingType('type', {
        GROUP_MEMBER: ObjectType(GroupMember),
        USER_MEMBER: ObjectType(UserMember),
    }))
    perms = ListAttribute(StringType())


class QuestionnaireVersion(AttributesMixin):
    created_at = DateTimeAttribute()
    created_by = ObjectAttribute(UserSuggestion)
    description = StringAttribute(nullable=True)
    event_uuid = StringAttribute()
    name = StringAttribute()
    updated_at = DateTimeAttribute()
    uuid = StringAttribute()


class QuestionnaireEvent(AttributesMixin):
    created_at = DateTimeAttribute()
    created_by = ObjectAttribute(UserSuggestion, nullable=True)
    type = StringAttribute(choices=EVENT_TYPES)
    uuid = StringAttribute()


class SetReplyEvent(QuestionnaireEvent):
    path = StringAttribute(nullable=True)
    value = Attribute(MappingType('type', {
        ANSWER_REPLY: ObjectType(AnswerReply),
        INTEGRATION_REPLY: ObjectType(IntegrationReply),
        ITEM_LIST_REPLY: ObjectType(ItemListReply),
        MULTI_CHOICE_REPLY: ObjectType(MultiChoiceReply),
        STRING_REPLY: ObjectType(StringReply),
    }), nullable=True)


class ClearReplyEvent(QuestionnaireEvent):
    path = StringAttribute()


class SetPhaseEvent(QuestionnaireEvent):
    phase = StringAttribute(nullable=True)


class SetLabelsEvent(QuestionnaireEvent):
    path = StringAttribute()
    value = ListAttribute(StringType())


class Indication(AttributesMixin):
    answered_questions = IntegerAttribute()
    unanswered_questions = IntegerAttribute()
    indication_type = StringAttribute(choices=INDICATIONS_TYPES)


class AnsweredIndication(Indication):
    pass


class PhasesAnsweredIndication(Indication):
    pass


class QuestionnaireReportDTO(AttributesMixin):
    indications = ListAttribute(MappingType('indication_type', {
        ANSWERED_INDICATION: ObjectType(AnsweredIndication),
        PHASES_ANSWERED_INDICATION: ObjectType(PhasesAnsweredIndication),
    }))


class QuestionnaireSimple(AttributesMixin):
    name = StringAttribute()
    uuid = StringAttribute()


class QuestionnaireCreateDTO(AttributesMixin):
    name = StringAttribute()
    package_id = StringAttribute()
    sharing = StringAttribute(choices=QUESTIONNAIRE_SHARING)
    visibility = StringAttribute(choices=QUESTIONNAIRE_VISIBILITIES)
    tag_uuids = ListAttribute(StringType(), default=[])
    template_id = StringAttribute(nullable=True, default=None)
    format_uuid = StringAttribute(nullable=True, default=None)


class QuestionnaireCreateFromTemplateDTO(AttributesMixin):
    name = StringAttribute()
    questionnaire_uuid = StringAttribute()
