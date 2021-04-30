import pytest


@pytest.fixture
def config(dsw_sdk):
    conf = dsw_sdk.app_config.get_config()
    orig_conf_data = conf.to_json()
    del orig_conf_data['uuid']
    yield conf
    for key, value in orig_conf_data.items():
        setattr(conf, key, value)
    conf.save()


def test_get_app_config(dsw_sdk):
    conf = dsw_sdk.app_config.get_config()
    # Assert some config attributes
    assert conf.authentication
    assert conf.created_at
    assert conf.privacy_and_support
    assert conf.template


def test_update_app_config(dsw_sdk, config):
    config.look_and_feel.app_title = 'New app title'
    config.privacy_and_support.support_repository_url = 'http://example.org'
    config.submission.enabled = True
    config.save()

    # Get the config again to ensure that the changes took place on the server
    new_config = dsw_sdk.app_config.get_config()
    assert new_config.look_and_feel.app_title == 'New app title'
    assert new_config.privacy_and_support.support_repository_url == 'http://example.org'
    assert new_config.submission.enabled is True
