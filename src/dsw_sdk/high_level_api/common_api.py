"""
Common classes for high-level APIs.
"""

from typing import Any, Callable, Dict, List, Optional, Type

from dsw_sdk.high_level_api.models.model import Model
from dsw_sdk.http_client.interface import (
    BadRequestError,
    HttpResponse,
    NotFoundError,
)


class NotInRegistryError(Exception):
    """
    Raised when attempting to pull an entity that is not present in the
    Data Stewardship Registry.
    """
    msg = '{} {} were not found in the registry.'

    def __init__(self, entity_types: str, ids: List[str]):
        super().__init__(self.msg.format(entity_types, ids))


class API:
    """
    Class defining common logic for all the other high-level APIs.
    Every subclass should define the :attr:`model_class` class attribute (it's
    the model class that the API is working with, e.g. :class:`~models.User`).
    """
    model_class: Type[Model]

    def __init__(self, sdk):
        self._sdk = sdk
        self._last_response: HttpResponse = None

    def _create_loaded(self, data: Dict[str, Any]) -> Model:
        return self.model_class(self._sdk, __update_attrs=data)

    def _get_one(self, func: Callable[[str], HttpResponse],
                 uuid: str) -> Model:
        data = func(uuid).json()
        return self._create_loaded(data)

    def _get_many_data(self, func: Callable[[Dict[str, Any]], HttpResponse],
                       data_key: str, **query_params) -> List[Dict[str, Any]]:
        self._last_response = func(query_params)
        response = self._last_response.json()
        data: List[Dict[str, Any]] = response['_embedded'][data_key]

        if query_params.get('page') is None:
            # If the user haven't specified `page` nor `size`, we can assume
            # that he/she wants all available results. But the API returns
            # at most 100 entries so we have to load to gradually. Same goes
            # for the case, when user specifies a size greater than 100.
            page = 1
            while (
                response['page']['number'] + 1 < response['page']['totalPages']
                and len(data) < query_params.get('size', 2**32)
            ):
                response = func({**query_params, 'page': page}).json()
                page += 1
                data.extend(response['_embedded'][data_key])

        return data

    def _get_many(self, func: Callable[[Dict[str, Any]], HttpResponse],
                  data_key: str, **query_params) -> List[Model]:
        data = self._get_many_data(func, data_key, **query_params)
        return [self._create_loaded(d) for d in data]

    def _create_new(self, **kwargs) -> Model:
        instance = self.model_class(self._sdk, **kwargs)
        instance.save()
        return instance

    def _delete_one(self, func: Callable[[str], HttpResponse], uuid: str):
        func(uuid)

    def _delete_many(self, func: Callable[[str], HttpResponse],
                     uuids: List[str]):
        for uuid in uuids:
            try:
                func(uuid)
            except NotFoundError:
                pass


class RegistryAPIMixin:
    """
    Mixin class providing common functionality for communicating with the
    Data Stewardship Registry.
    """

    @staticmethod
    def _pull(func: Callable[[str], HttpResponse],
              entity_types: str, ids: List[str]):
        not_found_ids = []
        for id_ in ids:
            try:
                func(id_)
            except BadRequestError as err:
                if "wasn't found in Registry" in err.msg:
                    not_found_ids.append(id_)
                elif 'already exists' in err.msg:
                    pass
                else:
                    raise
        if not_found_ids:
            raise NotInRegistryError(entity_types, not_found_ids)

    @staticmethod
    def _update(
        get_one: Callable[[str], Model],
        get_many: Callable[[], List[Model]],
        pull: Callable[[List[str]], None],
        ids: Optional[List[str]],
    ):
        if ids is None:
            entities = get_many()
        else:
            entities = [get_one(id_) for id_ in ids]

        remote_latest_ids = []
        for entity in entities:
            if (
                not entity.remote_latest_version
                or entity.remote_latest_version == entity.version
            ):
                continue
            remote_latest_id = (f'{entity.organization_id}:'
                                f'{entity.template_id}:'
                                f'{entity.remote_latest_version}')
            remote_latest_ids.append(remote_latest_id)

        pull(remote_latest_ids)
