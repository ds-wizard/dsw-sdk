# pylint: disable=R0901
"""
Module defining configuration of the whole library and implementing
the means of collecting the user config.

Configuration for each component is defined in separate class.
"""
from __future__ import annotations

import logging
import os
from collections.abc import Mapping
from typing import Any, Dict, Optional, Tuple, Union

import yaml

from dsw_sdk.common.attributes import (
    Attribute,
    AttributesMixin,
    BoolAttribute,
    StringAttribute,
)
from dsw_sdk.common.types import (
    DictType,
    IntegerType,
    NoneType,
    NumericType,
    StringType,
    TupleType,
    UnionType,
)


LOG_LEVELS = [logging.CRITICAL, logging.ERROR, logging.WARNING,
              logging.INFO, logging.DEBUG, logging.NOTSET]
# Extending the log levels with string representation of each level, so both
# e.g. `logging.INFO` and `20` are valid log level values.
LOG_LEVELS.extend([logging.getLevelName(level) for level in LOG_LEVELS])

MISSING_CONFIG_KEY_ERR = 'The config file `{}` does not contain the `{}` key.'

NUMERIC_PAIR_TYPE = TupleType(NumericType(), NumericType())
HEADERS_TYPE = DictType(StringType(), StringType())
TIMEOUT_TYPE = UnionType(NoneType(), NumericType(), NUMERIC_PAIR_TYPE)

Numeric = Union[int, float]
Headers = Dict[str, str]
Timeout = Union[None, Numeric, Tuple[Numeric, Numeric]]


class ComponentConfig(Mapping, AttributesMixin):
    """
    Base class for each component config.

    Implements all abstract methods of the :class:`collections.abc.Mapping`
    abstract class, so it can be used in following manner:

    .. code-block:: python

        >>> class Conf(ComponentConfig):
        ...     some_value = StringAttribute()

        >>> conf = Conf()
        >>> conf.some_value
        Traceback (most recent call last):
        ...
        dsw_sdk.common.attributes.AttributeNotSetError: ...
        >>> conf.some_value = 'foo'

        # Check if the value is set
        >>> 'some_value' in conf
        True

        # Get the item
        >>> conf.some_value
        'foo'
        >>> conf['some_value']
        'foo'

        # Get number of configured values
        >>> len(conf)
        1

        # Iterate over the config as dict
        >>> for value in conf.values(): pass
        >>> for key in conf.keys(): pass
        >>> for key, value in conf.items(): pass

        # Deconstruct the config to pass it as kwargs
        >>> def foo(**kwargs):
        ...     return kwargs['some_value']

        >>> foo(**conf)
        'foo'
    """
    def __contains__(self, item):
        return self.attrs().__contains__(item)

    def __getitem__(self, item):
        return self.attrs().__getitem__(item)

    def __iter__(self):
        return self.attrs().__iter__()

    def __len__(self):
        return self.attrs().__len__()


class HttpClientConfig(ComponentConfig):
    """
    Config for the HTTP client.
    """
    api_url: str = StringAttribute()
    email: str = StringAttribute()
    password: str = StringAttribute()
    enable_ssl: bool = BoolAttribute(default=True)
    auth_endpoint: str = StringAttribute(default='/tokens')
    headers: Headers = Attribute(HEADERS_TYPE, default={})
    default_timeout: Timeout = Attribute(TIMEOUT_TYPE,
                                         default=(6.05, 27))


class LoggerConfig(ComponentConfig):
    """
    Config for the Logger.
    """
    logger_name: str = StringAttribute(default='dsw_sdk')
    logger_level: str = Attribute(
        UnionType(IntegerType(), StringType()),
        default=logging.WARNING,
        choices=LOG_LEVELS,
    )
    logger_format: str = StringAttribute(
        default='[%(asctime)s] - %(name)s | %(levelname)s | %(message)s'
    )


class Config:
    """
    This class serves 2 purposes.

    It contains all the other "partial" configs. E.g.
    config objects for HTTP client or logger.

    It also collects user-defined configuration from env variables (prefixed
    by ``DSW_SDK``) and from file (YAML containing ``dsw_sdk`` section) passed
    in ``conf_file`` keyword argument. Then it merges these with all other
    values passed as keyword arguments, in following order (first takes
    precedence over the others):

        1) keyword arguments
        2) environment variables
        3) file config

    Example file config:

    .. code-block:: yaml

        dsw_sdk:
          enable_ssl: false
          auth_endpoint: '/auth'
          headers:
            'X-CUSTOM-HEADER': 'Custom value'
          default_timeout:
            - 6
            - 120

    """
    _FILE_SECTION = 'dsw_sdk'
    _ENV_PREFIX = 'DSW_SDK_'

    def __init__(self, **obj_config):
        """
        :param obj_config: arbitrary config values passed as keyword arguments;
                           if path is passed in ``conf_file``, it tries to load
                           the config values from a file
        """
        conf_file = obj_config.pop('conf_file', None)
        file_config = self._init_file_config(conf_file)
        env_config = self._init_env_config()
        conf = {**file_config, **env_config, **obj_config}

        self.http_client = HttpClientConfig(**conf)
        self.logger = LoggerConfig(**conf)

    @classmethod
    def _init_file_config(cls, conf_file: Optional[str]) -> Dict[str, Any]:
        if not conf_file:
            return {}

        with open(conf_file, 'r', encoding='utf-8') as file:
            file_config = yaml.safe_load(file)
            if cls._FILE_SECTION not in file_config:
                raise KeyError(
                    MISSING_CONFIG_KEY_ERR.format(conf_file, cls._FILE_SECTION)
                )
            return file_config.get(cls._FILE_SECTION, {})

    @classmethod
    def _init_env_config(cls) -> Dict[str, Any]:
        env_config = {}

        for k, v in os.environ.items():  # pylint: disable=C0103
            if not k.upper().startswith(cls._ENV_PREFIX):
                continue
            key = k.lstrip(cls._ENV_PREFIX).lower()
            env_config.update({key: v})

        return env_config
