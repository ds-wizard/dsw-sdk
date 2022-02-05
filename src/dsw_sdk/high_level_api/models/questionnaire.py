from dsw_sdk.common.attributes import (
    BoolAttribute,
    DateTimeAttribute,
    DictAttribute,
    ListAttribute,
    ObjectAttribute,
    StringAttribute,
)
from dsw_sdk.common.types import (
    ListType,
    MappingType,
    ObjectType,
    StringType,
)
from dsw_sdk.high_level_api.dto.common import (
    PackageSimpleDTO,
)
from dsw_sdk.high_level_api.dto.knowledge_model import KnowledgeModel
from dsw_sdk.high_level_api.dto.questionnaire import (
    ADD_COMMENT_EVENT,
    AddCommentEvent,
    CLEAR_REPLY_EVENT,
    ClearReplyEvent,
    DELETE_COMMENT_EVENT,
    DELETE_COMMENT_THREAD_EVENT,
    DeleteCommentEvent,
    DeleteCommentThreadEvent,
    EDIT_COMMENT_EVENT,
    EditCommentEvent,
    QUESTIONNAIRE_SHARING,
    QUESTIONNAIRE_STATES,
    QUESTIONNAIRE_VISIBILITIES,
    QuestionnaireCommentThread,
    QuestionnaireCreateDTO,
    QuestionnaireCreateFromTemplateDTO,
    QuestionnairePermRecordDTO,
    QuestionnaireVersion,
    REOPEN_COMMENT_THREAD_EVENT,
    RESOLVE_COMMENT_THREAD_EVENT,
    ReopenCommentThreadEvent,
    Reply,
    ResolveCommentThreadEvent,
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
    comment_threads_map = DictAttribute(
        StringType(),
        ListType(ObjectType(QuestionnaireCommentThread)),
    )
    created_at = DateTimeAttribute()
    creator_uuid = StringAttribute(nullable=True)
    description = StringAttribute(nullable=True)
    events = ListAttribute(MappingType('type', {
        ADD_COMMENT_EVENT: ObjectType(AddCommentEvent),
        CLEAR_REPLY_EVENT: ObjectType(ClearReplyEvent),
        DELETE_COMMENT_EVENT: ObjectType(DeleteCommentEvent),
        DELETE_COMMENT_THREAD_EVENT: ObjectType(DeleteCommentThreadEvent),
        EDIT_COMMENT_EVENT: ObjectType(EditCommentEvent),
        REOPEN_COMMENT_THREAD_EVENT: ObjectType(ReopenCommentThreadEvent),
        RESOLVE_COMMENT_THREAD_EVENT: ObjectType(ResolveCommentThreadEvent),
        SET_LABELS_EVENT: ObjectType(SetLabelsEvent),
        SET_PHASE_EVENT: ObjectType(SetPhaseEvent),
        SET_REPLY_EVENT: ObjectType(SetReplyEvent),
    }))
    format = ObjectAttribute(TemplateFormat, nullable=True)
    format_uuid = StringAttribute(nullable=True)
    is_template = BoolAttribute()
    knowledge_model = ObjectAttribute(KnowledgeModel)
    labels = DictAttribute(StringType(), ListType(StringType()))
    name = StringAttribute()
    package = ObjectAttribute(PackageSimpleDTO)
    package_id = StringAttribute()
    permissions = ListAttribute(ObjectType(QuestionnairePermRecordDTO))
    phase_uuid = StringAttribute(nullable=True)
    project_tags = ListAttribute(StringType())
    replies = DictAttribute(StringType(), ObjectType(Reply))
    selected_question_tag_uuids = ListAttribute(StringType())
    sharing = StringAttribute(choices=QUESTIONNAIRE_SHARING)
    state = StringAttribute(choices=QUESTIONNAIRE_STATES)
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
