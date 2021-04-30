from typing import Any, Callable, Dict, List, Type, TypeVar

from dsw_sdk.http_client.interface import (
    BadRequestError,
    HttpResponse,
    NotFoundError,
)


T = TypeVar('T')


class NotInRegistryError(Exception):
    msg = '{} {} were not found in the registry.'

    def __init__(self, entity_types: str, ids: List[str]):
        super().__init__(self.msg.format(entity_types, ids))


class API:
    model_class: Type[T]

    def __init__(self, sdk):
        self._sdk = sdk
        self._last_response: HttpResponse = None

    def _create_loaded(self, data: Dict[str, Any]) -> T:
        return self.model_class(self._sdk, __update_attrs=data)

    def _get_one(self, func: Callable[[str], HttpResponse],
                 uuid: str) -> T:
        data = func(uuid).json()
        return self._create_loaded(data)

    def _get_many(self, func: Callable[[Dict[str, Any]], HttpResponse],
                  data_key: str, **query_params) -> List[T]:
        self._last_response = func(query_params)
        response = self._last_response.json()
        data: List[Dict[str, Any]] = response['_embedded'][data_key]

        if query_params.get('page') is None:
            page = 1
            while (
                response['page']['number'] + 1 < response['page']['totalPages']
                and len(data) < query_params.get('size', 2**32)
            ):
                response = func({**query_params, 'page': page}).json()
                page += 1
                data.extend(response['_embedded'][data_key])

        return [self._create_loaded(d) for d in data]

    def _create_new(self, **kwargs) -> T:
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
    @staticmethod
    def _pull(func: Callable[[str], HttpResponse],
              entity_types: str, ids: List[str]):
        not_found_ids = []
        for id_ in ids:
            try:
                func(id_)
            except BadRequestError as e:
                if "wasn't found in Registry" in e.msg:
                    not_found_ids.append(id_)
                elif 'already exists' in e.msg:
                    pass
                else:
                    raise
        if not_found_ids:
            raise NotInRegistryError(entity_types, not_found_ids)

    @staticmethod
    def _update(
        get_one: Callable[[str], HttpResponse],
        get_many: Callable[[], HttpResponse],
        pull: Callable[[List[str]], None],
        ids: List[str],
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
