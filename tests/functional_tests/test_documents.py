from pytest_data import use_data

from dsw_sdk.high_level_api.dto.questionnaire import QuestionnaireSimple
from dsw_sdk.high_level_api.models.document import DONE_DOCUMENT_STATE


def _modify_documents(docs):
    """
    Setting the state to `done` for testing purposes. The
    comparison is otherwise very fragile and time dependent.
    """
    for doc in docs:
        doc.state = DONE_DOCUMENT_STATE


def test_get_document(dsw_sdk, document):
    loaded_document = dsw_sdk.documents.get_document(document.uuid)
    _modify_documents([document, loaded_document])

    assert loaded_document == document
    assert isinstance(loaded_document.questionnaire, QuestionnaireSimple)


@use_data(documents_data=[
    {'name': 'Test many'}, {'name': 'Test many'}, {'name': 'Test many foo'}]
)
def test_get_documents(dsw_sdk, documents):
    _modify_documents(documents)

    res = dsw_sdk.documents.get_documents()
    _modify_documents(res)
    assert len(res) >= 3
    assert documents[0] in res
    assert documents[1] in res
    assert documents[2] in res

    res = dsw_sdk.documents.get_documents(q='foo')
    _modify_documents(res)
    assert len(res) == 1
    assert res[0] == documents[-1]

    res = dsw_sdk.documents.get_documents(size=2)
    _modify_documents(res)
    assert len(res) == 2

    res = dsw_sdk.documents.get_documents(sort='uuid,desc', q='many')
    _modify_documents(res)
    assert res == sorted(documents, key=lambda q: q.uuid, reverse=True)
