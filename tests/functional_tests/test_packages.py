import pytest

from dsw_sdk.http_client.interface import NotFoundError


def test_pull_packages(dsw_sdk, registry_package_id):
    with pytest.raises(NotFoundError):
        dsw_sdk.api.get_package(registry_package_id)

    dsw_sdk.packages.pull_packages([registry_package_id])
    dsw_sdk.api.get_package(registry_package_id)
