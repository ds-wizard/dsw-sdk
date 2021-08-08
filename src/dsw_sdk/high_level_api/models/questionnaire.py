from dsw_sdk.common.attributes import (
    Alias,
    BoolAttribute,
    DateTimeAttribute,
    DictAttribute,
    ListAttribute,
    ObjectAttribute,
    StringAttribute,
)
from dsw_sdk.common.types import (
    MappingType,
    ObjectType,
    StringType,
)
from dsw_sdk.high_level_api.dto.common import (
    PackageSimpleDTO,
)
from dsw_sdk.high_level_api.dto.knowledge_model import KnowledgeModel
from dsw_sdk.high_level_api.dto.questionnaire import (
    CLEAR_REPLY_EVENT,
    ClearReplyEvent,
    QUESTIONNAIRE_SHARING,
    QUESTIONNAIRE_STATES,
    QUESTIONNAIRE_VISIBILITIES,
    QuestionnaireCreateDTO,
    QuestionnaireCreateFromTemplateDTO,
    QuestionnairePermRecordDTO,
    QuestionnaireVersion,
    Reply,
    SET_LABELS_EVENT,
    SET_PHASE_EVENT,
    SET_REPLY_EVENT,
    SetLabelsEvent,
    SetPhaseEvent,
    SetReplyEvent,
)
from dsw_sdk.high_level_api.dto.template import TemplateSimple
from dsw_sdk.high_level_api.models.document import Document
from dsw_sdk.high_level_api.models.model import ListOfModelsAttribute, Model
from dsw_sdk.high_level_api.models.templates.template import (
    TemplateFormat,
)


class Questionnaire(Model):
    created_at = DateTimeAttribute()
    creator_uuid = StringAttribute(nullable=True)
    description = StringAttribute(nullable=True)
    events = ListAttribute(MappingType('type', {
        SET_REPLY_EVENT: ObjectType(SetReplyEvent),
        CLEAR_REPLY_EVENT: ObjectType(ClearReplyEvent),
        SET_PHASE_EVENT: ObjectType(SetPhaseEvent),
        SET_LABELS_EVENT: ObjectType(SetLabelsEvent),
    }))
    format = ObjectAttribute(TemplateFormat, nullable=True)
    format_uuid = StringAttribute(nullable=True)
    is_template = BoolAttribute()
    knowledge_model = ObjectAttribute(KnowledgeModel)
    labels = DictAttribute(StringType(), StringType())
    phase_uuid = StringAttribute()
    name = StringAttribute()
    package = ObjectAttribute(PackageSimpleDTO)
    package_id = StringAttribute()
    permissions = ListAttribute(ObjectType(QuestionnairePermRecordDTO))
    replies = DictAttribute(StringType(), ObjectType(Reply))
    selected_tag_uuids = ListAttribute(StringType())
    sharing = StringAttribute(choices=QUESTIONNAIRE_SHARING)
    state = StringAttribute(choices=QUESTIONNAIRE_STATES)
    # TODO: Unite with `selected_tag_uuids`
    tag_uuids = Alias('selected_tag_uuids')
    template = ObjectAttribute(TemplateSimple, nullable=True)
    template_id = StringAttribute(nullable=True)
    updated_at = DateTimeAttribute()
    versions = ListAttribute(ObjectType(QuestionnaireVersion))
    visibility = StringAttribute(choices=QUESTIONNAIRE_VISIBILITIES)

    documents = ListOfModelsAttribute(Document, default=[])

    def _create(self):
        dto = QuestionnaireCreateDTO(**self.attrs())
        dto.validate()
        data = self._sdk.api.post_questionnaires(body=dto.to_json()).json()
        detail_data = self._sdk.api.get_questionnaire(
            qtn_uuid=data['uuid']
        ).json()
        self._update_attrs(**detail_data)

    def create_from_template(self, **kwargs):
        dto = QuestionnaireCreateFromTemplateDTO(**kwargs)
        dto.validate()
        created_data = self._sdk.api.post_questionnaires_from_template(
            body=dto.to_json()
        ).json()
        data = self._sdk.api.get_questionnaire(
            qtn_uuid=created_data['uuid']
        ).json()
        self._update_attrs(**data)

    def _update(self):
        raise NotImplementedError('Cannot update questionnaires')

    def _delete(self):
        raise NotImplementedError('Cannot delete questionnaires')
