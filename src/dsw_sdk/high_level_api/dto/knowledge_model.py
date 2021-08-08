from dsw_sdk.common.attributes import (
    AttributesMixin,
    DictAttribute,
    FloatAttribute,
    ListAttribute,
    ObjectAttribute,
    StringAttribute,
)
from dsw_sdk.common.types import MappingType, ObjectType, StringType


DATE_QUESTION_VALUE_TYPE = 'DateQuestionValueType'
NUMBER_QUESTION_VALUE_TYPE = 'NumberQuestionValueType'
STRING_QUESTION_VALUE_TYPE = 'StringQuestionValueType'
TEXT_QUESTION_VALUE_TYPE = 'TextQuestionValueType'
QUESTION_VALUE_TYPES = (
    DATE_QUESTION_VALUE_TYPE,
    NUMBER_QUESTION_VALUE_TYPE,
    STRING_QUESTION_VALUE_TYPE,
    TEXT_QUESTION_VALUE_TYPE,
)

INTEGRATION_QUESTION = 'IntegrationQuestion'
LIST_QUESTION = 'ListQuestion'
MULTI_CHOICE_QUESTION = 'MultiChoiceQuestion'
OPTIONS_QUESTION = 'OptionsQuestion'
VALUE_QUESTION = 'ValueQuestion'
QUESTION_TYPES = (
    INTEGRATION_QUESTION,
    LIST_QUESTION,
    MULTI_CHOICE_QUESTION,
    OPTIONS_QUESTION,
    VALUE_QUESTION,
)

RESOURCE_PAGE_REFERENCE = 'ResourcePageReference'
URL_REFERENCE = 'URLReference'
CROSS_REFERENCE = 'CrossReference'
REFERENCE_TYPES = (
    RESOURCE_PAGE_REFERENCE,
    URL_REFERENCE,
    CROSS_REFERENCE,
)


class Chapter(AttributesMixin):
    question_uuids = ListAttribute(StringType())
    text = StringAttribute(nullable=True)
    title = StringAttribute()
    uuid = StringAttribute()


class Question(AttributesMixin):
    expert_uuids = ListAttribute(StringType())
    question_type = StringAttribute(choices=QUESTION_TYPES)
    reference_uuids = ListAttribute(StringType())
    required_phase_uuid = StringAttribute(nullable=True)
    tag_uuids = ListAttribute(StringType())
    text = StringAttribute(nullable=True)
    title = StringAttribute()
    uuid = StringAttribute()


class OptionsQuestion(Question):
    answer_uuids = ListAttribute(StringType())


class MultiChoiceQuestion(Question):
    choice_uuids = ListAttribute(StringType())


class ListQuestion(Question):
    item_template_question_uuids = ListAttribute(StringType())


class ValueQuestion(Question):
    value_type = StringAttribute(choices=QUESTION_VALUE_TYPES)


class IntegrationQuestion(Question):
    props = DictAttribute(StringType(), StringType())


class MetricMeasure(AttributesMixin):
    metric_uuid = StringAttribute()
    measure = FloatAttribute()
    weight = FloatAttribute()


class Answer(AttributesMixin):
    advice = StringAttribute(nullable=True)
    follow_up_uuids = ListAttribute(StringType())
    label = StringAttribute()
    metric_measures = ListAttribute(ObjectType(MetricMeasure))
    uuid = StringAttribute()


class Choice(AttributesMixin):
    label = StringAttribute()
    uuid = StringAttribute()


class Expert(AttributesMixin):
    email = StringAttribute()
    name = StringAttribute()
    uuid = StringAttribute()


class Reference(AttributesMixin):
    uuid = StringAttribute()
    reference_type = StringAttribute(choices=REFERENCE_TYPES)


class ResourcePageReference(Reference):
    short_uuid = StringAttribute()


class URLReference(Reference):
    label = StringAttribute()
    url = StringAttribute()


class CrossReference(Reference):
    description = StringAttribute()
    target_uuid = StringAttribute()


class Integration(AttributesMixin):
    id = StringAttribute()
    item_url = StringAttribute()
    logo = StringAttribute()
    name = StringAttribute()
    props = ListAttribute(StringType())
    request_body = StringAttribute()
    request_headers = DictAttribute(StringType(), StringType())
    request_method = StringAttribute()
    request_url = StringAttribute()
    response_id_field = StringAttribute()
    response_list_field = StringAttribute()
    response_name_field = StringAttribute()
    uuid = StringAttribute()


class Tag(AttributesMixin):
    color = StringAttribute()
    description = StringAttribute(nullable=True)
    name = StringAttribute()
    uuid = StringAttribute()


class KnowledgeModelEntities(AttributesMixin):
    answers = DictAttribute(StringType(), ObjectType(Answer))
    chapters = DictAttribute(StringType(), ObjectType(Chapter))
    choices = DictAttribute(StringType(), ObjectType(Choice))
    experts = DictAttribute(StringType(), ObjectType(Expert))
    integrations = DictAttribute(StringType(), ObjectType(Integration))
    questions = DictAttribute(StringType(), MappingType('question_type', {
        OPTIONS_QUESTION: ObjectType(OptionsQuestion),
        MULTI_CHOICE_QUESTION: ObjectType(MultiChoiceQuestion),
        LIST_QUESTION: ObjectType(ListQuestion),
        VALUE_QUESTION: ObjectType(ValueQuestion),
        INTEGRATION_QUESTION: ObjectType(IntegrationQuestion),
    }))
    references = DictAttribute(StringType(), MappingType('reference_type', {
        RESOURCE_PAGE_REFERENCE: ObjectType(ResourcePageReference),
        URL_REFERENCE: ObjectType(URLReference),
        CROSS_REFERENCE: ObjectType(CrossReference),
    }))
    tags = DictAttribute(StringType(), ObjectType(Tag))


class KnowledgeModel(AttributesMixin):
    chapter_uuids = ListAttribute(StringType())
    entities = ObjectAttribute(KnowledgeModelEntities)
    integration_uuids = ListAttribute(StringType())
    tag_uuids = ListAttribute(StringType())
    uuid = StringAttribute()
