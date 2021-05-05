"""
Packages high-level API.
"""

from typing import List

from dsw_sdk.high_level_api.common_api import API, RegistryAPIMixin


class PackageAPI(API, RegistryAPIMixin):
    """
    API for the Package entities.

    This class provides a method for pulling new versions of packages
    (knowledge models). Other methods might be added in the future.

    Example usage:

    .. code-block:: python

        api = PackageAPI(...)

        # Pull specified packages from the Data Stewardship Registry
        api.pull_packages(['dsw:package1:2.2.0', 'dsw:package2:1.0.0'])
    """

    def pull_packages(self, ids: List[str]):
        """
        Pulls given packages from the Data Stewardship Registry, so they
        become available in the DSW instance.

        :param ids: IDs of the packages you want to pull form the registry
        """
        self._pull(self._sdk.api.post_package_pull, 'Packages', ids)

    def update_packages(self, ids: List[str] = None):
        # This will be implemented in future; we need to define the package
        # model first.
        raise NotImplementedError('Updating packages is not yet implemented')
