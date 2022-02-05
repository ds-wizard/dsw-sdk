from dsw_sdk.common.types import ObjectType
from dsw_sdk.common.attributes import (
    DateTimeAttribute,
    ListAttribute,
    ObjectAttribute,
    StringAttribute,
)
from dsw_sdk.high_level_api.dto.questionnaire import QuestionnaireSimple
from dsw_sdk.high_level_api.dto.template import TemplateSimpleDTO
from dsw_sdk.high_level_api.models.model import Model
from dsw_sdk.high_level_api.dto.common import SubmissionDTO


DONE_DOCUMENT_STATE = 'DoneDocumentState'
ERROR_DOCUMENT_STATE = 'ErrorDocumentState'
IN_PROGRESS_DOCUMENT_STATE = 'InProgressDocumentState'
QUEUED_DOCUMENT_STATE = 'QueuedDocumentState'
DOCUMENT_STATES = (
    DONE_DOCUMENT_STATE,
    ERROR_DOCUMENT_STATE,
    IN_PROGRESS_DOCUMENT_STATE,
    QUEUED_DOCUMENT_STATE,
)


class Document(Model):
    content_type = StringAttribute(nullable=True)
    created_at = DateTimeAttribute()
    creator_uuid = StringAttribute(nullable=True)
    filename = StringAttribute(nullable=True)
    format_uuid = StringAttribute()
    name = StringAttribute()
    questionnaire = ObjectAttribute(QuestionnaireSimple, nullable=True)
    questionnaire_event_uuid = StringAttribute(nullable=True)
    state = StringAttribute(choices=DOCUMENT_STATES)
    submissions = ListAttribute(ObjectType(SubmissionDTO))
    template = ObjectAttribute(TemplateSimpleDTO)

    def _create(self):
        raise NotImplementedError('Cannot create documents')

    def _update(self):
        raise NotImplementedError('Cannot update documents')

    def _delete(self):
        raise NotImplementedError('Cannot delete documents')
