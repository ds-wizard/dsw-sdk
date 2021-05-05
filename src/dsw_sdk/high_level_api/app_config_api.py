"""
App config high-level API.
"""

from __future__ import annotations

from dsw_sdk.high_level_api.common_api import API
from dsw_sdk.high_level_api.models.app_config import AppConfig


class AppConfigAPI(API):
    """
    API for the App config "entity".

    There is just one GET and one PUT method on the DSW API, so we can
    only return the app config values, updated it and then save it on
    the remote server once again.
    """
    model_class = AppConfig

    def get_config(self) -> AppConfig:
        """
        Get app config from the server.

        :return: object containing DSW app config
        """
        config_data = self._sdk.api.get_configs_app().json()
        return AppConfig(self._sdk, __update_attrs=config_data)
