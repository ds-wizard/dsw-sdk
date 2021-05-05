"""
Documents high-level API.
"""
from __future__ import annotations

from typing import List

from dsw_sdk.high_level_api.common_api import API
from dsw_sdk.high_level_api.models.document import Document
from dsw_sdk.http_client.interface import NotFoundError


class DocumentAPI(API):
    """
    API for the Document entities.

    For now, there are just two methods for getting one or many documents
    (as others were not yet required, but might be implemented in the future).

    Example usage:

    .. code-block:: python

        api = DocumentAPI(...)

        # Get one document by UUID
        doc = api.get_document('some-uuid-1234')

        # Get all documents for a given questionnaire
        docs = api.get_documents(questionnaire_uuid='q-uuid-5')

        # Get page number 1 (each page having 10 documents) of documents
        # containing the "foo" string, sorted by the UUID attribute in the
        # ascending order
        docs = api.get_documents(q='foo', page=1, size=10, sort='uuid,asc')
    """
    model_class = Document

    def get_document(self, uuid: str) -> Document:
        """
        Retrieves one document, identified by it's UUID.

        :param uuid: universally unique identifier of the document

        :return: object representing a document
        """
        res = self.get_documents()
        for document in res:
            if document.uuid == uuid:
                return document
        raise NotFoundError(self._last_response)

    def get_documents(self, questionnaire_uuid: str = None,
                      **query_params) -> List[Document]:
        """
        Retrieves list of documents.
        Possibly identified by the questionnaire to which they belong to.

        :param questionnaire_uuid: UUID of the questionnaire whose documents
            we want to fetch
        :param query_params: optional query params: ``q``, ``size``, ``page``
            and ``sort``

        :return: list of objects, each representing a document
        """
        if questionnaire_uuid:
            query_params['questionnaire_uuid'] = questionnaire_uuid
        documents = self._get_many(self._sdk.api.get_documents,
                                   'documents', **query_params)
        return documents
