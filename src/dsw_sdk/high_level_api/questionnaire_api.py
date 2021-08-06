"""
Questionnaires high-level API.
"""
from __future__ import annotations

from typing import List

from dsw_sdk.high_level_api.common_api import API
from dsw_sdk.high_level_api.models.questionnaire import Questionnaire


class QuestionnaireAPI(API):
    """
    API for the Questionnaire entities.

    For now, there are just two methods for getting one or many questionnaires
    (as others were not yet required, but might be implemented in the future).

    Example usage:

    .. code-block:: python

        api = QuestionnaireAPI(...)

        # Get one questionnaire by UUID
        q = api.get_questionnaire('some-uuid-1234')

        # Get page number 1 (each page having 10 questionnaires) of
        # questionnaires containing the "foo" string, sorted by the UUID
        # attribute in the ascending order
        qs = api.get_questionnaires(q='foo', page=1, size=10, sort='uuid,asc')
    """
    model_class = Questionnaire

    def get_questionnaire(self, uuid: str) -> Questionnaire:
        """
        Retrieves one questionnaire, identified by it's UUID.
        Also loading all of it's related documents.

        :param uuid: universally unique identifier of the questionnaire

        :return: object representing a questionnaire
        """
        questionnaire = self._get_one(self._sdk.api.get_questionnaire, uuid)
        documents_page = self._sdk.api.get_questionnaire_documents(uuid).json()
        questionnaire._update_attrs(
            package_id=questionnaire.package.id,
            documents=documents_page['_embedded']['documents']
        )
        return questionnaire

    def get_questionnaires(self, **query_params) -> List[Questionnaire]:
        """
        Retrieves list of questionnaires.
        Also loading all related documents.

        :param query_params: optional query params ``q``, ``size``, ``page``
            and ``sort``

        :return: list of objects, each representing a questionnaire
        """
        questionnaires = self._get_many_data(self._sdk.api.get_questionnaires,
                                             'questionnaires', **query_params)
        return [self.get_questionnaire(questionnaire['uuid'])
                for questionnaire in questionnaires]

    def create_questionnaire(self, **kwargs) -> Questionnaire:
        """
        Create a new questionnaire (custom).

        :param kwargs: all the data needed for the questionnaire creation

        :return: object representing the newly created questionnaire
        """
        return self._create_new(**kwargs)

    def create_questionnaire_from_template(
            self, name: str, questionnaire_uuid: str
    ) -> Questionnaire:
        """
        Create a new questionnaire from a template

        :param name: name of the new questionnaire
        :param questionnaire_uuid: uuid of the template questionnaire

        :return: object representing the newly created questionnaire
        """
        questionnaire = self.model_class(self._sdk)
        questionnaire.create_from_template(
            name=name,
            questionnaire_uuid=questionnaire_uuid,
        )
        return questionnaire
