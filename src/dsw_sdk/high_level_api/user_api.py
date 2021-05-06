"""
Users high-level API.
"""
from __future__ import annotations

from typing import Dict, List

from dsw_sdk.high_level_api.common_api import API
from dsw_sdk.high_level_api.dto.questionnaire import USER_MEMBER
from dsw_sdk.high_level_api.models.questionnaire import Questionnaire
from dsw_sdk.high_level_api.models.user import User


class UserAPI(API):
    """
    API for the User entities.

    Supports all of the CRUD operations.

    Example usage:

    .. code-block:: python

        api = UserAPI(...)

        # Get one user by UUID
        user = api.get_user('some-user-uuid')

        # Get all users
        users = api.get_users()

        # Get page number 1 (each page having 10 users) of users
        # containing the "foo" string, sorted by the UUID attribute in the
        # ascending order
        users = api.get_users(q='foo', page=1, size=10, sort='uuid,asc')

        # Create user
        user = api.create_user(first_name='John', ...)

        # Delete user
        api.delete_user(user.uuid)

        # Delete list of users
        api.delete_users(['some-user-uuid', 'another-user-123'])
    """
    model_class = User

    def _load_questionnaires(
        self,
        user_uuids: List[str],
    ) -> Dict[str, List[Questionnaire]]:
        """
        For a given list of user UUIDs, loads all of their questionnaires and
        associated documents.
        """
        user_questionnaires: Dict[str, List[Questionnaire]] = {
            uuid: [] for uuid in user_uuids
        }

        questionnaires = self._sdk.questionnaires.get_questionnaires()
        for quest in questionnaires:
            for perm in quest.permissions:
                if (
                    perm.member.type == USER_MEMBER
                    and perm.member.uuid in user_uuids
                ):
                    user_questionnaires[perm.member.uuid].append(quest)

        return user_questionnaires

    def get_user(self, uuid: str) -> User:
        """
        Retrieves one user, identified by it's UUID.
        Also loading all his/her related questionnaires and documents.

        :param uuid: user identifier

        :return: object representing a user
        """
        user = self._get_one(self._sdk.api.get_user, uuid)
        questionnaire_lookup = self._load_questionnaires([uuid])
        user._update_attrs(questionnaires=questionnaire_lookup[uuid])
        return user

    def get_users(self, **query_params) -> List[User]:
        """
        Retrieves list of users.
        Also loading all related questionnaires and documents.

        :param query_params: optional query params: ``q``, ``size``, ``page``
            and ``sort``

        :return: list of objects, each representing a user
        """
        users = self._get_many(self._sdk.api.get_users,
                               'users', **query_params)
        user_uuids = [user.uuid for user in users]
        questionnaire_lookup = self._load_questionnaires(user_uuids)
        for user in users:
            user_questionnaires = questionnaire_lookup[user.uuid]
            user._update_attrs(questionnaires=user_questionnaires)
        return users

    def create_user(self, **kwargs) -> User:
        """
        Creates a user with given data on the DSW server.

        :param kwargs: all the data needed for the user creation

        :return: object representing the new user
        """
        return self._create_new(**kwargs)

    def delete_user(self, uuid: str):
        """
        Deletes a user from the DSW server.

        :param uuid: UUID of the user to delete
        """
        self._delete_one(self._sdk.api.delete_user, uuid)

    def delete_users(self, uuids: List[str]):
        """
        Deletes multiple users on the DSW server, identified by UUIDs.

        :param uuids: UUIDs of users to delete
        """
        self._delete_many(self._sdk.api.delete_user, uuids)
