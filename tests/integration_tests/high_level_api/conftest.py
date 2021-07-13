import pytest


@pytest.fixture(autouse=True)
def auto_clean(clean):
    """
    Using empty "autouse" fixture to ensure that the `clean` fixture will be
    called automatically for the whole testing module (before each test).
    """
    pass
