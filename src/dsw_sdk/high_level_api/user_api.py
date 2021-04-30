from typing import Dict, List

from dsw_sdk.high_level_api.api import API
from dsw_sdk.high_level_api.dto.questionnaire import USER_MEMBER
from dsw_sdk.high_level_api.models.questionnaire import Questionnaire
from dsw_sdk.high_level_api.models.user import User


class UserAPI(API):
    model_class = User

    def _load_questionnaires(
        self,
        user_uuids: List[str],
    ) -> Dict[str, List[Questionnaire]]:
        user_questionnaires = {uuid: [] for uuid in user_uuids}

        questionnaires = self._sdk.questionnaires.get_questionnaires()
        for q in questionnaires:
            for perm in q.permissions:
                if (
                    perm.member.type == USER_MEMBER
                    and perm.member.uuid in user_uuids
                ):
                    user_questionnaires[perm.member.uuid].append(q)

        return user_questionnaires

    def get_user(self, uuid: str) -> User:
        user = self._get_one(self._sdk.api.get_user, uuid)
        questionnaire_lookup = self._load_questionnaires([uuid])
        user._update_attrs(questionnaires=questionnaire_lookup[uuid])
        return user

    def get_users(self, **query_params) -> List[User]:
        users = self._get_many(self._sdk.api.get_users,
                               'users', **query_params)
        user_uuids = [user.uuid for user in users]
        questionnaire_lookup = self._load_questionnaires(user_uuids)
        for user in users:
            user_questionnaires = questionnaire_lookup[user.uuid]
            user._update_attrs(questionnaires=user_questionnaires)
        return users

    def create_user(self, **kwargs) -> User:
        return self._create_new(**kwargs)

    def delete_user(self, uuid: str):
        self._delete_one(self._sdk.api.delete_user, uuid)

    def delete_users(self, uuids: List[str]):
        self._delete_many(self._sdk.api.delete_user, uuids)
