from pytest_data import use_data


def test_get_questionnaire(dsw_sdk, questionnaire):
    uuid = questionnaire.uuid
    loaded_questionnaire = dsw_sdk.questionnaires.get_questionnaire(uuid)

    assert loaded_questionnaire == questionnaire
    assert loaded_questionnaire.documents == []


@use_data(questionnaires_data=[
    {'name': 'Test many'}, {'name': 'Test many'}, {'name': 'Test many foo'}]
)
def test_get_many_questionnaires(dsw_sdk, questionnaires):
    res = dsw_sdk.questionnaires.get_questionnaires()
    assert len(res) >= 3
    assert questionnaires[0] in res
    assert questionnaires[1] in res
    assert questionnaires[2] in res

    res = dsw_sdk.questionnaires.get_questionnaires(q='foo')
    assert len(res) == 1
    assert res[0] == questionnaires[2]

    res = dsw_sdk.questionnaires.get_questionnaires(size=2)
    assert len(res) == 2

    res = dsw_sdk.questionnaires.get_questionnaires(sort='uuid,asc', q='many')
    assert res == sorted(questionnaires, key=lambda q: q.uuid)


def test_create_questionnaire_via_api(dsw_sdk, questionnaire_data):
    questionnaire = dsw_sdk.questionnaires.create_questionnaire(
        **questionnaire_data
    )
    assert questionnaire.uuid is not None


def test_create_questionnaire_from_template_via_api(
        dsw_sdk, questionnaire_template_data
):
    questionnaire = dsw_sdk.questionnaires.create_questionnaire_from_template(
        **questionnaire_template_data
    )
    assert questionnaire.uuid is not None
