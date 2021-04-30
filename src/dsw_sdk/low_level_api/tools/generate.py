import os
import re
import sys
from typing import Any, Dict, List

import requests
from jinja2 import Environment, PackageLoader

from dsw_sdk.common.utils import to_snake_case


def getattr_list(list_: List[Dict[str, Any]], attr: str) -> List[Any]:
    return [item.get(attr) for item in list_]


def to_python_type(api_type: str) -> str:
    return {
        'string': 'str',
        'integer': 'int',
    }[api_type]


def to_singular(word: str) -> str:
    if not word.endswith('s'):
        # Suppose that all plurals end with an `s` letter... (:
        return word
    return {
        'branches': 'branch',
    }.get(word, word[:-1])


class APIDefinition:
    def __init__(self):
        swagger_url = sys.argv[-1]
        json_data = requests.get(swagger_url).json()
        self._paths: Dict[str, Any] = json_data['paths']
        self._definitions: Dict[str, Any] = json_data['definitions']

    @staticmethod
    def _get_func_name(path: str) -> str:
        # Path always starts with a `/` character
        path = path[1:]

        path_parts = []
        for path_part in path.split('/'):
            # Parts of the path starting with `{` are variable query params
            if path_part.startswith('{'):
                # We want to transform the last entry (word preceding
                # the variable query param) into singular form
                path_parts[-1] = to_singular(path_parts[-1])
            else:
                path_parts.append(path_part)

        return '_'.join(path_parts).replace('-', '_')

    @staticmethod
    def _get_params(endpoint_info: dict, kind: str) -> List[Dict[str, Any]]:
        return [
            param
            for param in endpoint_info.get('parameters', [])
            if param['in'] == kind
        ]

    def _get_body_params(self, endpoint_info: dict) -> List[Dict[str, str]]:
        """
        This method is WIP and needs to be finished.
        """
        body_params = self._get_params(endpoint_info, 'body')
        if not body_params:
            return []

        dto_name = body_params[0]['schema'].get('$ref', '').split('/')[-1]
        if not dto_name:
            return []
        dto = self._definitions[dto_name]
        # TODO: Do something with optional parameters
        return [
            {'name': key, 'type': value.get('type')}
            for key, value in dto['properties'].items()
            if key in dto['required']
        ]

    def _get_func_params(self, endpoint_info) -> str:
        func_params = self._get_params(endpoint_info, 'path')
        func_params = [
            f'{to_snake_case(param["name"])}: {to_python_type(param["type"])}'
            for param in func_params
        ]
        if self._get_params(endpoint_info, 'body'):
            func_params.append('body: Dict[str, Any]')
        if self._get_params(endpoint_info, 'query'):
            func_params.append('query_params: Optional[Dict[str, Any]] = None')
        return ', '.join(['self', *func_params, '**kwargs'])

    @staticmethod
    def _pythonize_path(path: str) -> str:
        return re.sub(r'({\w+})', lambda m: to_snake_case(m.group(1)), path)

    def parse(self):
        functions = []
        for path, all_methods in self._paths.items():
            for http_method, info in all_methods.items():
                functions.append({
                    'http_method': http_method,
                    'func_name': self._get_func_name(path),
                    'func_params': self._get_func_params(info),
                    'query_params': self._get_params(info, 'query'),
                    'body': self._get_body_params(info),
                    'path': self._pythonize_path(path),
                })

        parent_dir = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                os.path.pardir,
            )
        )
        with open(f'{parent_dir}/api.py', 'w') as file:
            file.write(template.render(functions=functions))


if __name__ == '__main__':
    env = Environment(loader=PackageLoader('templates', ''))
    template = env.get_template('test.py.jinja')
    APIDefinition().parse()
