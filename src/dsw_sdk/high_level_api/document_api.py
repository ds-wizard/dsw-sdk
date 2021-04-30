from typing import List

from dsw_sdk.high_level_api.api import API
from dsw_sdk.high_level_api.models.document import Document
from dsw_sdk.http_client.interface import NotFoundError


class DocumentAPI(API):
    model_class = Document

    def get_document(self, uuid: str) -> Document:
        res = self.get_documents()
        for document in res:
            if document.uuid == uuid:
                return document
        raise NotFoundError(self._last_response)

    def get_documents(self, questionnaire_uuid: str = None,
                      **query_params) -> List[Document]:
        if questionnaire_uuid:
            query_params['questionnaire_uuid'] = questionnaire_uuid
        documents = self._get_many(self._sdk.api.get_documents,
                                   'documents', **query_params)
        return documents
