import pytest

from am4.utils.db import init

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(scope="session", autouse=True)
def initialize_database():
    init()
    yield
