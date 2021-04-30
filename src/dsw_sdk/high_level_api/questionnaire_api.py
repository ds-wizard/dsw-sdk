from typing import List

from dsw_sdk.high_level_api.api import API
from dsw_sdk.high_level_api.models.questionnaire import Questionnaire


class QuestionnaireAPI(API):
    model_class = Questionnaire

    def get_questionnaire(self, uuid: str) -> Questionnaire:
        questionnaire = self._get_one(self._sdk.api.get_questionnaire, uuid)
        documents_page = self._sdk.api.get_questionnaire_documents(uuid).json()
        questionnaire._update_attrs(
            documents=documents_page['_embedded']['documents']
        )
        return questionnaire

    def get_questionnaires(self, **query_params) -> List[Questionnaire]:
        questionnaires = self._get_many(self._sdk.api.get_questionnaires,
                                        'questionnaires', **query_params)
        return [self.get_questionnaire(questionnaire.uuid)
                for questionnaire in questionnaires]
