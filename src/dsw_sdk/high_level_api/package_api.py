from typing import List

from dsw_sdk.high_level_api.api import API, RegistryAPIMixin


class PackageAPI(API, RegistryAPIMixin):

    def pull_packages(self, ids: List[str]):
        self._pull(self._sdk.api.post_package_pull, 'Packages', ids)

    def update_packages(self, ids: List[str] = None):
        # This will be implemented in future; we need to define the package
        # model first.
        raise NotImplementedError('Updating packages is not yet implemented')
